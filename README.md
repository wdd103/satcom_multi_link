# 航空卫星通信场景平台

基于本地网页、Python 和 STK 12 的卫星通信场景配置与数据生产工具。支持飞机、TLE 卫星、地面网关、上下行链路、大气损耗、机体遮挡及下行同频干扰，并导出链路时间线供 OMNeT++ 分组仿真读取。

更新日期：2026-11-25。当前交付以[交付说明](satcom_platform/docs/产品交付说明_当前状态_2026-11-25.md)、代码和各运行目录的 manifest 为准。

## 当前功能

| 功能 | 已实现内容 |
|---|---|
| 本地网页 | 项目打开、新建、另存、草稿编辑、校验、保存、STK 运行与结果下载。 |
| 航迹与卫星 | 规范航迹 CSV、测试航迹生成、本地 TLE 读取、卫星勾选；运行时纳入已启用卫星。 |
| 多飞机与传感器 | 导入已有 STK 飞机/传感器模板；批量复制航迹、模型、传感器、收发机、天线和链路；上传/选择 `.bmsk` 并启停机体遮挡。 |
| 通信链路 | 飞机上/下行与地面网关馈电上/下行；STK Simple 收发机预算，输出 C/N、Eb/No、BER。 |
| 场景传播损耗 | 雨衰、气体吸收、云雾、对流层闪烁四个网页独立开关及参数；读取 STK 各项损耗。 |
| 卫星干扰 | 下行非服务同频卫星接收功率聚合；检查几何与选定传感器可见性，使用收发两端离轴方向图；输出 SINR、干扰后 BER 近似及各源贡献。 |
| 天线与多普勒 | APENST818V01 统一公式、独立参数；IDEAL 理想补偿与 FIXED 固定调谐。天线页采用可横向滚动的宽表格，输入框已加宽。 |
| 运行进度 | 网页与 STK Message Viewer 显示计算阶段、百分比、对象/链路和计数。 |
| OMNeT++ | 导出 `omnet_link_timeline.csv`；首版三节点模型读取通断、传播时延与固定配置速率。 |

## 快速启动

离线校验和网页需要 Python 3.10+；STK 仿真还需要 Windows、可用的 STK 12 Communications 能力及 pywin32。已在本机 STK 12.6 上联调，其他安装环境需验证。

在仓库根目录的 PowerShell 执行：

```powershell
python -m pip install -e ./satcom_platform
$env:PYTHONPATH = (Resolve-Path ./satcom_platform/src).Path
# 需要运行 STK 时安装
python -m pip install pywin32
python -m satcom_platform.web --project ./satcom_platform/examples/minimal_project --port 8765
```

打开 [http://127.0.0.1:8765/](http://127.0.0.1:8765/)。服务只监听本机回环地址。无需运行 STK 即可编辑和离线校验项目。

1. 打开示例或自己的项目，检查航迹、TLE、卫星选择和场景 UTC 时段。
2. 在「飞机与传感器」导入模板或批量复制飞机，选择默认可见性传感器和遮挡文件。
3. 配置收发机、天线、链路、大气损耗及下行干扰，保存并验证。
4. 在「仿真检查与运行」启动 STK；卫星数量限制填 0 表示全部已启用卫星。限制卫星数量也会限制干扰源集合。
5. 在「结果」下载 CSV、清单和场景包；将所需链路时间线交给 OMNeT++。

当前示例配置包含 AC1、AC2 和 GW1，最低仰角为 5°，场景为 2026-11-12 02:00–02:10 UTC。这些是演示参数；实际运行以保存配置为准。示例 TLE 比场景早约 30 天，不应用于可信飞行覆盖结论。

## 工程目录

```text
satcom_multi_link/
├─ satcom_platform/          # Python 配置、网页、STK 计算与时间线导出
│  ├─ src/satcom_platform/
│  ├─ examples/minimal_project/
│  │  ├─ config/            # YAML、收发机/天线/卫星 CSV
│  │  ├─ input/             # 航迹与本地 TLE
│  │  ├─ assets/            # 飞机模型、模板和遮挡文件
│  │  └─ runs/              # 每次运行的结果目录
│  ├─ tests/
│  ├─ scripts/              # STK 探针与联调脚本
│  └─ docs/
├─ omnet/                   # OMNeT++ 三节点分组仿真
└─ docs/                    # 原需求规格与项目汇报
```

## 输出和计算口径

| 输出 | 用途 |
|---|---|
| `aircraft_state.csv` | 飞机位置采样。 |
| `link_geometry.csv`、`gateway_geometry.csv` | 飞机/网关与卫星的几何可见性、角度和距离。 |
| `aircraft_sensor_visibility.csv` | 几何可见性、传感器可见性及交集，辅助排查机体遮挡。 |
| `link_budget.csv` | 通信 Access、各项大气损耗、STK 原始 C/N、Eb/No、BER，以及干扰后指标与多普勒字段。 |
| `interference_contributions.csv` | 每个同频干扰源的离轴角、增益和接收功率。 |
| `omnet_link_timeline.csv` | 半开时间区间内的可用性、传播时延和固定配置速率。 |
| `manifest.json`、`rf_environment.json`、`antenna_patterns.json` | 运行配置、输入追溯、模型和参数记录。 |
| `scenario.sc`、`scenario_bundle.zip` | STK 场景及相关模型、模板、遮挡文件和结果。 |

不可用或无计算依据的量可能为空；空值与数值零含义不同。例如无干扰时功率 W 为 0，而不可用链路的质量指标为空。具体字段以对应输出与专题说明为准。

## 模型边界

- 服务链路假设理想对准，飞机/网关峰值增益 15 dBi，卫星 20 dBi；下行干扰使用两端离轴增益。STK 场景使用 Simple 等效设备，平台计算离轴聚合，尚非原生 CommSystem 干扰报告。
- APENST818V01 的 30°/20°是分段角，属于原参数的宽波束适配，并非实测方向图或半功率波束宽度。
- 四项大气模型给出统计衰减，不生成真实天气或随机衰落序列。电离层、通用多径模型尚未提供本项目网页开关与运行集成。
- `.bmsk` 支持已有文件导入和应用；未自动从任意模型生成。更换机体、缩放或安装位置后需重新生成匹配文件；未从航迹自动推导真实俯仰/横滚历程。
- 同频干扰采用非服务卫星持续发射假设；理想多普勒补偿不模拟捕获失败或跟踪误差。
- 数据率采用配置值，不按香农公式或 SINR 自动调速。干扰后 BER 为未编码 BPSK 的高斯干扰近似；当前 OMNeT++ 不据此随机丢包。
- 平台可导出多飞机、多卫星数据；OMNeT++ 当前只运行单飞机—单卫星—单网关。多飞机导出需先筛选目标四条有向链路，不能直接视为已支持多飞机网络或自动多星切换。

## 验证与进一步使用

```powershell
$env:PYTHONPATH = (Resolve-Path ./satcom_platform/src).Path
python -m satcom_platform validate --project ./satcom_platform/examples/minimal_project --offline --json
Push-Location ./satcom_platform
python -m unittest discover -s tests -q
node tests/test_rf_controls.cjs
node tests/test_fleet_controls.cjs
Pop-Location
```

Python 测试覆盖配置与计算逻辑，Node.js 用于前端控件检查；原生 STK 联调需要另行执行探针。2026-11-25 已有 39 项 Python 测试、前端检查和独立 STK 联调记录，详见交付说明；这不代表每次文档修改都重新跑完整仿真。

- [Python 平台 README](satcom_platform/README.md)：配置、运行、排查和验证命令。
- [OMNeT++ README](omnet/README.md)：构建、时间线接入和分组统计。
- [当前交付说明](satcom_platform/docs/产品交付说明_当前状态_2026-11-25.md)。
- [大气传播损耗](satcom_platform/docs/rf_environment.md)。
- [同频干扰、天线方向图与多普勒](satcom_platform/docs/downlink_interference.md)。
- [飞机、传感器与机体遮挡](satcom_platform/docs/fleet_body_mask.md)。
- [OMNeT++ 文件接口](satcom_platform/docs/omnet_interface_v1.md)。
- [原开发需求规格（历史）](docs/开发需求与实现规格_2026-11-12.md)：设计目标，不是当前已交付能力清单。
