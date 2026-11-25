# Satcom Platform：网页配置与 STK 链路计算

Python 子项目负责 YAML/CSV/TLE 校验、航迹生成、本地网页、STK 12 COM 场景构建、几何/通信预算、大气损耗、下行干扰、机体遮挡与 OMNeT++ 时间线导出。项目总览见[根目录 README](../README.md)，当前范围见[2026-11-25 交付说明](docs/产品交付说明_当前状态_2026-11-25.md)。

## 安装与启动

以下 PowerShell 命令均在 `satcom_platform` 目录执行：

```powershell
python -m pip install -e .
# 运行 STK 需要；离线校验不需要
python -m pip install pywin32
python -m satcom_platform.web --project examples/minimal_project --port 8765
```

Python 版本要求 3.10+。基础依赖 PyYAML、Flask 由安装命令安装；原生 STK 计算另需 Windows、已安装的 STK 12 及 Communications 能力。当前本机验证版本为 STK 12.6，未承诺任意版本兼容。不安装包时可先设置 `$env:PYTHONPATH = 'src'`。

打开 [http://127.0.0.1:8765/](http://127.0.0.1:8765/)。网页只监听本机回环地址；服务进程需保持运行。PySide6 桌面 GUI 尚未实现。

## 网页使用

| 页面 | 用途 |
|---|---|
| 总览 | 项目路径、配置与校验摘要。 |
| 航迹输入 | 规范 CSV 上传与编辑、生成测试航迹；生成器不推导真实飞机姿态。 |
| TLE 卫星 | 读取本地 TLE，管理卫星 CSV 与启用选择。 |
| 飞机与传感器 | 从已有 `.sc` 导入模板、批量复制飞机和链路；配置传感器与 `.bmsk`。 |
| 场景参数 | 时间、步长、最低仰角；雨衰、气体吸收、云雾、对流层闪烁开关；干扰与多普勒配置。 |
| 收发机与链路 | 设备参数、上/下行与馈电链路、C/N 或 SINR 门限、可见性传感器覆盖。 |
| 天线配置 | 可横向滚动的宽表格；普通输入框最小 190 px，外部方向图路径最小 280 px；各行独立设置参数。 |
| 规范文件导入 | 已支持的规范输入说明；任意来源文件字段映射尚未实现。 |
| 仿真检查与运行 | 保存、校验后启动 STK；卫星数量限制 0 表示全部已启用卫星。 |
| 结果 | 查看运行状态、进度和下载结果。 |

编辑先进入草稿，点击顶部保存后用于下一次运行。导入模板会复制资源到项目 `assets`；批量复制单次最多新增 100 架，并复制相应航迹、收发机、天线与飞机链路。零位置偏移表示航迹重合。已有 `.bmsk` 适用于对应机体、缩放和安装设置；关闭遮挡文件仍保留传感器视场。

运行时 STK Message Viewer 显示 `[SATCOM run_id]` 消息。若未显示，可打开 **View → Message Viewer → All Messages**。网页约每 2.5 秒刷新进度；百分比为阶段加权估计，计数来自实际处理。完成场景和压缩包保存后才达到 100%；失败保留错误与最后进度。

## 项目文件

```text
project/
├─ config/scenario.yaml             # 场景、传播、链路、网关、飞机/传感器与输出配置
├─ config/transmitter_receiver.csv  # 设备及天线引用
├─ config/antenna.csv               # 天线参数
├─ config/satellite_config.csv      # 卫星与启用选择
├─ input/aircraft_track.csv         # 多飞机位置时序
├─ input/satellites.tle             # 本地轨道要素
├─ assets/                         # 模型、原生模板和遮挡文件
└─ runs/<run_id>/                   # 结果与状态
```

路径通常相对项目根目录解析，ID 区分大小写。CSV 使用规范字段和单位；时间采用 UTC，经纬度为度，高度/距离为米，频率/带宽为 Hz，数据率为 bit/s，发射功率为 dBW。

无卫星 CSV 时，网页从 TLE 唯一 NORAD ID 生成候选并默认启用，保存后生成 CSV。有 CSV 时以 CSV 为清单来源；更新 TLE 后仍需检查 NORAD 引用和场景时段。勾选和保存不会改写 TLE。被禁用卫星的链路模板仍可能保留并产生提示。

当前示例配置有 AC1、AC2、GW1、6 条链路和 12 副天线，场景最低仰角 5°；它会随用户编辑变化。示例 TLE 比场景早约 30 天，数值主要验证流程；不要把告警阈值调大视为提高轨道精度。

## 传播、增益、干扰与遮挡

- 四项大气损耗由 STK 原生模型计算，独立开关和参数见[传播模型说明](docs/rf_environment.md)。统计损耗与真实天气时间序列不同，高空飞机路径可能不经过雨云。
- APENST818V01 收发统一公式：飞机/网关峰值 15 dBi、分段角 30°；卫星 20 dBi、分段角 20°；效率 0.7、B=25。A 留空自动保持分段连续，对应约 41.629276 和 38.051295。分段角不是半功率波束宽度，当前为宽波束适配。
- STK Simple 等效设备提供服务链路理想对准预算；平台用两端离轴方向图修正跨路径功率并在线性域聚合非服务同频卫星干扰。不是原生 CommSystem 报告。详见[干扰与方向图](docs/downlink_interference.md)。
- 干扰源需通过几何最低仰角和飞机选定传感器可见性；服务链路也检查遮挡。传感器配置与姿态限制见[机体遮挡说明](docs/fleet_body_mask.md)。
- IDEAL 开启原生自动跟频，并把理想补偿残余频偏置零；STK 原始多普勒频移单独记录。FIXED 为固定调谐。

## 运行输出

| 文件 | 内容 |
|---|---|
| `status.json` | RUNNING、COMPLETE 或 FAILED，以及阶段、进度、错误和文件清单。 |
| `aircraft_state.csv` | 飞机位置采样。 |
| `link_geometry.csv`、`gateway_geometry.csv` | 原始几何可见性、角度和距离。 |
| `aircraft_sensor_visibility.csv` | `geometric_access`、`sensor_access`、`effective_access` 和遮挡启用标记。 |
| `link_budget.csv` | 链路 Access、选定传感器、大气损耗、C/N、Eb/No、BER、多普勒与下行干扰后指标。 |
| `interference_contributions.csv` | 各同频干扰源的离轴角、增益和功率。 |
| `omnet_link_timeline.csv` | 半开时间区间内的通断、传播时延、固定配置速率及质量指标。 |
| `manifest.json`、`rf_environment.json`、`antenna_patterns.json` | 配置、模型、参数和输入追溯。 |
| `scenario.sc`、`scenario_bundle.zip`、`*.e`、`antenna_*.ant` | 原生场景、相关资源、外部星历及方向图采样。 |

STK 原始 `cn_db / ebno_db / ber` 与平台的 `sinr_db / ebni_db / ber_with_interference` 分开保留。空值不等于零：不可见链路的预算可能为空；无干扰时功率 W 为零，对应 dBW 或 C/I 的无穷量留空。原生几何、传感器和最终通信 Access 是不同判定。

STK sidecar 可能保留源 TLE 的绝对路径，跨机器使用场景包时应检查。旧运行的输入、字段与模型以自己的 manifest 为准，不能用当前配置反推历史运行。

## CLI 与验证

```powershell
python -m satcom_platform validate --project examples/minimal_project --offline --json
python -m satcom_platform validate --project examples/minimal_project --preflight --json
python -m unittest discover -s tests -q
node tests/test_rf_controls.cjs
node tests/test_fleet_controls.cjs
```

CLI 当前提供 `validate` 和 `generate-track`。STK 仿真通过网页启动；`--preflight` 是配置检查及模型假设提示，不是原生许可和数据提供器的完整验收。测试航迹生成会写入指定项目，应在自己的测试副本上使用：

```powershell
python -m satcom_platform generate-track --help
```

以下脚本会运行原生 STK 联调，需相应本机环境；用途与独立场景行为请先查看脚本，不是离线测试：

```powershell
python scripts/probe_stk.py
python scripts/probe_rf_environment.py
python scripts/probe_downlink_interference.py
python scripts/probe_fleet_masks.py
```

同日已有 39 项 Python 测试、前端控件检查及 STK 联调记录，具体范围见[交付说明](docs/产品交付说明_当前状态_2026-11-25.md)。本次 README 更新不表示重新执行完整仿真。

## 限制与文档

数据率为配置值，不按香农容量或 SINR 自动调整；干扰后 BER 为未编码 BPSK 高斯近似，不等于分组丢失率。尚无真实姿态自动推导、通用多径/电离层集成、自动 `.bmsk` 生成或原生方向天线 CommSystem 集成。多飞机数据可导出，但 OMNeT++ 首版仍是固定三节点拓扑，需筛选目标飞机/卫星/网关对应四条链路。

- [OMNeT++ 接入](../omnet/README.md)与[文件接口](docs/omnet_interface_v1.md)。
- [当前交付说明](docs/产品交付说明_当前状态_2026-11-25.md)。
- [安装说明](docs/setup.md)与[模型限制](docs/limitations.md)。
- [M2 核验记录（历史）](docs/stk_m2.md)及[2026-11-16 交付（历史）](docs/产品交付说明_当前状态_2026-11-16.md)。
