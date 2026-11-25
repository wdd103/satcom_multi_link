# STK → OMNeT++ 分组仿真

更新日期：2026-11-25。工程总览见[根目录 README](../README.md)，数据生成方法见[平台 README](../satcom_platform/README.md)。

本工程从 `satcom_platform` 一次 STK 运行的 `omnet_link_timeline.csv` 读取四条有向链路，只选择 `omnetpp.ini` 指定的一颗卫星。拓扑为飞机、卫星中继和地面网关；飞机与网关各自生成业务包。卫星在两个方向分别使用有限队列。链路状态在时间表区间起点更新，包含通断、传播时延和固定配置速率。当前不根据 STK BER 随机丢包，也不实现重传或多星切换。

## 构建与运行

已在 `D:\LeStoreDownload\omnetpp-6.5.0-windows-x86_64\omnetpp-6.5.0` 的 OMNeT++ 6.5.0 上编译、运行。进入该安装包的命令环境后，从本目录运行：

```sh
opp_makemake -f --deep -o SatcomBridge
make -j4
./SatcomBridge -u Cmdenv -n ned omnetpp.ini
```

Windows 上本次生成的可执行文件为 `out/clang-release/SatcomBridge.exe`，运行命令为 `./out/clang-release/SatcomBridge.exe -u Cmdenv -n ned omnetpp.ini`。工程只依赖 OMNeT++ 本身。运行前将 `omnetpp.ini` 中的 `timelineFile` 指向目标 STK 运行目录；相对路径以本目录为起点。当前默认使用双星验证运行中的 `SAT41918`。本机 OMNeT++ shell 未自动提供 `python3` 和 `clang++` 路径；构建时将 `tools/` 与该安装包的 `tools/win32.x86_64/clang64/bin` 加入 PATH。

`omnetpp.ini` 当前指向历史验证运行，新的大气损耗、干扰和遮挡设置不会追溯修改该文件。要使用新模型结果，先在网页保存并完成新的 STK 运行，再替换时间线路径。

当前控制器按卫星筛选，**不会自动跳过同一卫星下其他飞机的链路**。平台批量飞机导出后，需先筛选目标飞机、卫星、网关的四条有向链路，保证每个方向每个区间只有一条记录；直接导入多飞机时间线会因端点不匹配而报错。通过 `*.controller.aircraftId`、`*.controller.satelliteId`、`*.controller.gatewayId` 设置所选 ID，默认分别为 AC1、SAT41918、GW1。仿真时长与业务起止也应匹配时间线。

可以先用 Python 检查筛选后的时间表：

```sh
python tests/check_timeline.py ../satcom_platform/examples/minimal_project/runs/20261118T020000Z-aabbccdd/omnet_link_timeline.csv --aircraft AC1 --satellite SAT41918 --gateway GW1
```

## 物理层参数如何影响分组仿真

读取器使用 `available`、`propagation_delay_s`、`capacity_bps` 更新链路。STK/平台侧已经用几何、传感器遮挡及配置的 C/N、SINR 门限决定可用性，因此损耗和干扰可通过链路通断影响网络。当前读取器不直接使用 BER/SINR 随机丢包，也不基于香农公式调速。`capacity_bps` 为可用链路的配置数据率，不是测得吞吐量。

## 统计口径

`Endpoint` 分别记录产生、进入首跳、首跳不可用或忙导致的丢弃、到达、接收字节、平均端到端时延和按完整仿真时长计算的吞吐量。`SatelliteRelay` 记录向两端转发、队列溢出丢弃和结束时仍在队列中的包数。输出写入 `results/` 下的 OMNeT++ 标量及向量文件。

首跳忙时丢弃；中继第二跳不可用时缓存，满 100 包后丢弃。信道变化只影响变化后发送的包；已在途的包继续按发送时的参数到达。仿真在 600 秒结束，结束时在途包不计入已接收。链路区间和物理量定义见[接口说明](../satcom_platform/docs/omnet_interface_v1.md)。

当前飞机、网关和卫星 ID 由控制器参数指定，拓扑固定一个卫星节点。后续多星需要增加卫星实例及切换逻辑。

## 本机历史运行结果

2026-11-18 使用 STK 运行 `20261118T020000Z-aabbccdd` 的 `SAT41918` 时间表完成 600 秒仿真，结果见 `results/General-0.sca`。飞机产生 6000 包，首跳进入 1900 包，网关接收 1900 包；网关产生 6000 包，首跳进入 1800 包，飞机接收 1800 包。卫星队列溢出为 0。按完整 600 秒计算，网关接收吞吐量 30.4 kbps，飞机接收吞吐量 28.8 kbps。平均端到端时延分别约 46.05 ms 和 45.87 ms。
