# STK → OMNeT++ 首版模型

本工程从 `satcom_platform` 一次 STK 运行的 `omnet_link_timeline.csv` 读取四条有向链路，只选择 `omnetpp.ini` 指定的一颗卫星。拓扑为飞机、卫星中继和地面网关；飞机与网关各自生成业务包。卫星在两个方向分别使用有限队列。链路状态在时间表区间起点更新，包含通断、传播时延和固定配置速率。当前不根据 STK BER 随机丢包，也不实现重传或多星切换。

## 构建与运行

已在 `D:\LeStoreDownload\omnetpp-6.5.0-windows-x86_64\omnetpp-6.5.0` 的 OMNeT++ 6.5.0 上编译、运行。进入该安装包的命令环境后，从本目录运行：

```sh
opp_makemake -f --deep -o SatcomBridge
make -j4
./SatcomBridge -u Cmdenv -n ned omnetpp.ini
```

Windows 上本次生成的可执行文件为 `out/clang-release/SatcomBridge.exe`，运行命令为 `./out/clang-release/SatcomBridge.exe -u Cmdenv -n ned omnetpp.ini`。工程只依赖 OMNeT++ 本身。运行前将 `omnetpp.ini` 中的 `timelineFile` 指向目标 STK 运行目录；相对路径以本目录为起点。当前默认使用双星验证运行中的 `SAT41918`。本机 OMNeT++ shell 未自动提供 `python3` 和 `clang++` 路径；构建时将 `tools/` 与该安装包的 `tools/win32.x86_64/clang64/bin` 加入 PATH。

可以先用 Python 检查时间表：

```sh
python tests/check_timeline.py ../satcom_platform/examples/minimal_project/runs/20261118T020000Z-aabbccdd/omnet_link_timeline.csv
```

## 统计口径

`Endpoint` 分别记录产生、进入首跳、首跳不可用或忙导致的丢弃、到达、接收字节、平均端到端时延和按完整仿真时长计算的吞吐量。`SatelliteRelay` 记录向两端转发、队列溢出丢弃和结束时仍在队列中的包数。输出写入 `results/` 下的 OMNeT++ 标量及向量文件。

首跳忙时丢弃；中继第二跳不可用时缓存，满 100 包后丢弃。信道变化只影响变化后发送的包；已在途的包继续按发送时的参数到达。仿真在 600 秒结束，结束时在途包不计入已接收。链路区间和物理量定义见 `../satcom_platform/docs/omnet_interface_v1.md`。

当前飞机、网关和卫星 ID 由控制器参数指定，拓扑固定一个卫星节点。后续多星需要增加卫星实例及切换逻辑。

## 本机运行结果

2026-11-18 使用 STK 运行 `20261118T020000Z-aabbccdd` 的 `SAT41918` 时间表完成 600 秒仿真，结果见 `results/General-0.sca`。飞机产生 6000 包，首跳进入 1900 包，网关接收 1900 包；网关产生 6000 包，首跳进入 1800 包，飞机接收 1800 包。卫星队列溢出为 0。按完整 600 秒计算，网关接收吞吐量 30.4 kbps，飞机接收吞吐量 28.8 kbps。平均端到端时延分别约 46.05 ms 和 45.87 ms。
