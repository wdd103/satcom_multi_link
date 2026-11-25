# OMNeT++ 链路文件接口 v1

STK 运行完成后，在同一运行目录生成 `omnet_link_timeline.csv`。位于工作区根目录 `omnet/` 的首版 OMNeT++ 模型读取该文件，选择一颗卫星运行两跳分组仿真。

## 场景与链路

`scenario.yaml` 的 `gateways` 定义地面网关 WGS84 大地纬度、经度和高度（米）。示例网关 `GW1` 位于 31.2304°N、121.4737°E、高度 10 m；这只是演示位置。网关在 STK 中为 Facility。`FEEDER_DOWNLINK` 表示卫星到网关，`FEEDER_UPLINK` 表示网关到卫星。示例中的 `FD1`、`FU1` 与原有飞机链路 `U1`、`D1` 组成四条有向链路。卫星设备仍按配置模板复制到每颗已启用卫星。

## 文件约定

每行代表一个链路实例在半开区间 `[start_s,end_s)` 的状态。`start_s=0` 对应清单的 `scenario_start_utc`。最后一个 STK 采样点位于场景终点，不形成额外区间。`run_id` 为运行目录名；`link_instance_id` 为 `link_id:satellite_id`。`source_id`、`target_id` 是有向链路端点。

| 字段 | 约定 |
|---|---|
| `available` | STK 通信 Access、几何最低仰角、选定飞机传感器约束与配置的最小 C/N 门限同时满足时为 `true`；存在 SINR 结果时还检查最小 SINR 门限（未单独配置时沿用 C/N 门限）。 |
| `range_m`, `propagation_delay_s` | 可用时填写；时延为距离除以 299792458 m/s。不可用时留空。 |
| `capacity_bps` | 可用时为发射机配置的固定数据率；不可用时为 0。它不是实测吞吐量。 |
| `ebno_db`, `cn_db`, `ber` | 可用时为 STK `Link Information` 采样值；不可用时留空。BER 仅作为物理层估计。 |
| `modulation` | 当前固定写 `STK_DEFAULT_BPSK`，表示尚未配置显式调制。 |

`manifest.json` 记录接口版本、行数、采样间隔和网关配置。`gateway_geometry.csv` 提供网关到卫星的可见性、仰角和距离。所有新文件均进入 `scenario_bundle.zip`。

OMNeT++ 侧应逐行按 `start_s` 安排状态更新，并按 `source_id`、`target_id` 连接有向链路；端到端业务需分别判断两段链路状态。10 秒采样采用区间起点状态保持，不推断采样点之间的通断事件。

新增质量列包括 `sinr_db`、`ebni_db`、`ber_with_interference`，与原始 STK 指标分开保留。当前 OMNeT++ 读取器只用可用性、传播时延和配置速率控制信道，不直接用这些质量列随机丢包或调速。

多飞机时间线必须先筛选为目标飞机、卫星和网关对应的四条有向链路；当前控制器只按卫星过滤，不会自动忽略其他飞机。详见[OMNeT++ README](../../omnet/README.md)。

## 历史验证记录

2026-11-18 本机 STK 12 单星和双星运行均完成。双星运行 `examples/minimal_project/runs/20261118T020000Z-aabbccdd` 输出 480 个时间区间；其中飞机下行、飞机上行、馈电下行和馈电上行分别有 24、19、23、18 个可用区间。该运行用于验证接口和数据流，示例 TLE 与理想跟踪假设沿用原项目。
