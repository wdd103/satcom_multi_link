#include <omnetpp.h>

#include <algorithm>
#include <array>
#include <cmath>
#include <fstream>
#include <stdexcept>
#include <map>
#include <sstream>
#include <string>
#include <vector>

using namespace omnetpp;

namespace {

struct LinkSample {
    double start = 0;
    double end = 0;
    bool available = false;
    double delay = 0;
    double rate = 0;
};

std::vector<std::string> fields(const std::string& line) {
    std::vector<std::string> result;
    std::stringstream stream(line);
    std::string field;
    while (std::getline(stream, field, ',')) result.push_back(field);
    if (!line.empty() && line.back() == ',') result.emplace_back();
    return result;
}

const std::array<std::string, 4> directions = {"UPLINK", "FEEDER_DOWNLINK", "FEEDER_UPLINK", "DOWNLINK"};
const std::array<std::string, 4> senderNames = {"aircraft", "satellite", "gateway", "satellite"};
const std::array<std::string, 4> gateNames = {"out", "toGateway", "out", "toAircraft"};

} // namespace

class LinkController : public cSimpleModule {
  private:
    std::array<std::vector<LinkSample>, 4> samples;
    std::array<cDatarateChannel *, 4> channels{};
    cMessage *timer = nullptr;
    size_t index = 0;
    std::string runId;

  protected:
    int numInitStages() const override { return 2; }
    void initialize(int stage) override {
        if (stage != 1) return;
        const std::string path = par("timelineFile").stdstringValue();
        const std::string satelliteId = par("satelliteId").stdstringValue();
        const std::string aircraftId = par("aircraftId").stdstringValue();
        const std::string gatewayId = par("gatewayId").stdstringValue();
        std::ifstream input(path);
        if (!input) throw cRuntimeError("Cannot open timeline: %s", path.c_str());
        std::string line;
        if (!std::getline(input, line)) throw cRuntimeError("Empty timeline");
        const auto header = fields(line);
        std::map<std::string, size_t> column;
        for (size_t i = 0; i < header.size(); ++i) column[header[i]] = i;
        for (const char *name : {"run_id", "link_instance_id", "direction", "source_id", "target_id", "start_s", "end_s", "available", "propagation_delay_s", "capacity_bps"})
            if (!column.count(name)) throw cRuntimeError("Timeline column missing: %s", name);
        int lineNumber = 1;
        while (std::getline(input, line)) {
            ++lineNumber;
            if (line.empty()) continue;
            auto value = fields(line);
            if (value.size() != header.size()) throw cRuntimeError("Timeline row %d has wrong width", lineNumber);
            auto get = [&](const char *name) -> const std::string& { return value[column.at(name)]; };
            const auto suffix = ":" + satelliteId;
            const auto& instance = get("link_instance_id");
            if (instance.size() < suffix.size() || instance.substr(instance.size() - suffix.size()) != suffix) continue;
            const auto& currentRun = get("run_id");
            if (runId.empty()) runId = currentRun;
            if (runId != currentRun) throw cRuntimeError("Mixed run IDs in timeline");
            const auto& direction = get("direction");
            auto found = std::find(directions.begin(), directions.end(), direction);
            if (found == directions.end()) throw cRuntimeError("Unknown direction on row %d", lineNumber);
            const size_t slot = found - directions.begin();
            const auto source = slot == 0 ? aircraftId : slot == 2 ? gatewayId : satelliteId;
            const auto target = slot == 1 ? gatewayId : slot == 3 ? aircraftId : satelliteId;
            if (get("source_id") != source || get("target_id") != target)
                throw cRuntimeError("Unexpected endpoints on row %d", lineNumber);
            LinkSample sample;
            try {
                sample.start = std::stod(get("start_s"));
                sample.end = std::stod(get("end_s"));
                const auto& state = get("available");
                if (state != "true" && state != "false") throw std::invalid_argument("available");
                sample.available = state == "true";
                if (sample.available) {
                    sample.delay = std::stod(get("propagation_delay_s"));
                    sample.rate = std::stod(get("capacity_bps"));
                }
            } catch (const std::exception&) { throw cRuntimeError("Invalid numeric value on row %d", lineNumber); }
            if (!std::isfinite(sample.start) || !std::isfinite(sample.end) || sample.end <= sample.start ||
                (sample.available && (!std::isfinite(sample.delay) || sample.delay < 0 || !std::isfinite(sample.rate) || sample.rate <= 0)))
                throw cRuntimeError("Invalid interval on row %d", lineNumber);
            samples[slot].push_back(sample);
        }
        for (size_t slot = 0; slot < 4; ++slot) {
            auto& sequence = samples[slot];
            if (sequence.empty()) throw cRuntimeError("Timeline has no %s samples for %s", directions[slot].c_str(), satelliteId.c_str());
            std::sort(sequence.begin(), sequence.end(), [](const auto& a, const auto& b) { return a.start < b.start; });
            if (std::abs(sequence.front().start) > 1e-9) throw cRuntimeError("Timeline must start at zero");
            for (size_t i = 1; i < sequence.size(); ++i)
                if (std::abs(sequence[i].start - sequence[i-1].end) > 1e-9)
                    throw cRuntimeError("Gap or overlap in %s timeline", directions[slot].c_str());
            cModule *sender = getParentModule()->getSubmodule(senderNames[slot].c_str());
            channels[slot] = check_and_cast<cDatarateChannel *>(sender->gate(gateNames[slot].c_str())->getTransmissionChannel());
            channels[slot]->setDisabled(true);
        }
        for (size_t slot = 1; slot < 4; ++slot) {
            if (samples[slot].size() != samples[0].size()) throw cRuntimeError("Selected link directions have different grids");
            for (size_t i = 0; i < samples[0].size(); ++i)
                if (std::abs(samples[slot][i].start - samples[0][i].start) > 1e-9 ||
                    std::abs(samples[slot][i].end - samples[0][i].end) > 1e-9)
                    throw cRuntimeError("Selected link directions have different grids");
        }
        apply();
        timer = new cMessage("next-link-sample");
        timer->setSchedulingPriority(-1);
        if (samples[0].size() > 1) scheduleAt(samples[0][1].start, timer);
        EV_INFO << "Loaded " << samples[0].size() << " intervals from run " << runId << " for " << satelliteId << "\n";
    }

    void apply() {
        for (size_t slot = 0; slot < 4; ++slot) {
            const auto& sample = samples[slot][index];
            auto *channel = channels[slot];
            if (sample.available) {
                channel->setDelay(sample.delay);
                channel->setDatarate(sample.rate);
            }
            channel->setDisabled(!sample.available);
        }
    }

    void handleMessage(cMessage *message) override {
        if (message != timer) throw cRuntimeError("Unexpected controller message");
        ++index;
        apply();
        if (index + 1 < samples[0].size()) scheduleAt(samples[0][index + 1].start, timer);
    }

    void finish() override {
        recordScalar("timelineIntervals", static_cast<double>(samples[0].size()));
    }

  public:
    ~LinkController() override { cancelAndDelete(timer); }
};
Define_Module(LinkController);

class Endpoint : public cSimpleModule {
  private:
    cMessage *generation = nullptr;
    long generated = 0, admitted = 0, droppedNoLink = 0, received = 0;
    double totalDelay = 0;
    long receivedBytes = 0;

  protected:
    void initialize() override {
        if (par("sendEnabled").boolValue()) {
            generation = new cMessage("generate");
            scheduleAt(SimTime(par("trafficStart").doubleValue()), generation);
        }
    }
    void handleMessage(cMessage *message) override {
        if (message == generation) {
            if (simTime() >= SimTime(par("trafficStop").doubleValue())) return;
            ++generated;
            auto *channel = check_and_cast<cDatarateChannel *>(gate("out")->getTransmissionChannel());
            if (channel->isDisabled() || channel->isBusy()) {
                ++droppedNoLink;
            } else {
                auto *packet = new cPacket("traffic");
                packet->setByteLength(par("packetBytes").intValue());
                packet->setTimestamp();
                send(packet, "out");
                ++admitted;
            }
            const simtime_t next = simTime() + SimTime(par("sendInterval").doubleValue());
            if (next < SimTime(par("trafficStop").doubleValue())) scheduleAt(next, generation);
        } else {
            auto *packet = check_and_cast<cPacket *>(message);
            ++received;
            receivedBytes += packet->getByteLength();
            const double delay = (simTime() - packet->getTimestamp()).dbl();
            totalDelay += delay;
            emit(registerSignal("endToEndDelay"), delay);
            delete packet;
        }
    }
    void finish() override {
        recordScalar("generated", generated);
        recordScalar("admitted", admitted);
        recordScalar("droppedNoLink", droppedNoLink);
        recordScalar("received", received);
        recordScalar("receivedBytes", receivedBytes);
        recordScalar("meanEndToEndDelay_s", received ? totalDelay / received : 0);
        recordScalar("throughput_bps", simTime() > 0 ? 8.0 * receivedBytes / simTime().dbl() : 0);
    }
  public:
    ~Endpoint() override { cancelAndDelete(generation); }
};
Define_Module(Endpoint);

class SatelliteRelay : public cSimpleModule {
  private:
    std::array<cQueue, 2> queues;
    std::array<cMessage *, 2> timers{};
    std::array<long, 2> forwarded{}, droppedOverflow{};

  protected:
    void initialize() override {
        for (int i = 0; i < 2; ++i) {
            timers[i] = new cMessage(i == 0 ? "retry-to-gateway" : "retry-to-aircraft");
        }
    }
    void trySend(int side) {
        auto *channel = check_and_cast<cDatarateChannel *>(gate(side == 0 ? "toGateway" : "toAircraft")->getTransmissionChannel());
        if (!queues[side].isEmpty() && !channel->isDisabled() && !channel->isBusy()) {
            send(check_and_cast<cPacket *>(queues[side].pop()), side == 0 ? "toGateway" : "toAircraft");
            ++forwarded[side];
        }
        if (!queues[side].isEmpty() && !timers[side]->isScheduled()) {
            simtime_t next = channel->isBusy() ? channel->getTransmissionFinishTime() : simTime() + SimTime(par("retryInterval").doubleValue());
            if (next <= simTime()) next = simTime() + SimTime(par("retryInterval").doubleValue());
            scheduleAt(next, timers[side]);
        }
    }
    void handleMessage(cMessage *message) override {
        for (int side = 0; side < 2; ++side)
            if (message == timers[side]) { trySend(side); return; }
        const int side = message->getArrivalGate() == gate("fromAircraft") ? 0 : 1;
        if (queues[side].getLength() >= par("queueCapacity").intValue()) {
            ++droppedOverflow[side];
            delete message;
        } else {
            queues[side].insert(message);
            trySend(side);
        }
    }
    void finish() override {
        recordScalar("forwardedToGateway", forwarded[0]);
        recordScalar("forwardedToAircraft", forwarded[1]);
        recordScalar("droppedOverflowToGateway", droppedOverflow[0]);
        recordScalar("droppedOverflowToAircraft", droppedOverflow[1]);
        recordScalar("queuedToGatewayAtEnd", queues[0].getLength());
        recordScalar("queuedToAircraftAtEnd", queues[1].getLength());
    }
  public:
    ~SatelliteRelay() override {
        for (auto *timer : timers) cancelAndDelete(timer);
        for (auto& queue : queues) while (!queue.isEmpty()) delete queue.pop();
    }
};
Define_Module(SatelliteRelay);
