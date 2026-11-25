simple LinkController
{
    parameters:
        string timelineFile;
        string satelliteId = default("SAT41918");
        string aircraftId = default("AC1");
        string gatewayId = default("GW1");
}

simple Endpoint
{
    parameters:
        bool sendEnabled = default(true);
        int packetBytes = default(1200);
        double sendInterval @unit(s) = default(0.1s);
        double trafficStart @unit(s) = default(0s);
        double trafficStop @unit(s) = default(600s);
    gates:
        input in;
        output out;
}

simple SatelliteRelay
{
    parameters:
        int queueCapacity = default(100);
        double retryInterval @unit(s) = default(1s);
    gates:
        input fromAircraft;
        input fromGateway;
        output toAircraft;
        output toGateway;
}

network SatcomNetwork
{
    submodules:
        controller: LinkController;
        aircraft: Endpoint;
        satellite: SatelliteRelay;
        gateway: Endpoint;
    connections:
        aircraft.out --> airToSat: ned.DatarateChannel --> satellite.fromAircraft;
        satellite.toGateway --> satToGateway: ned.DatarateChannel --> gateway.in;
        gateway.out --> gatewayToSat: ned.DatarateChannel --> satellite.fromGateway;
        satellite.toAircraft --> satToAir: ned.DatarateChannel --> aircraft.in;
}
