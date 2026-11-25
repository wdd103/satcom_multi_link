# 航空卫星通信场景自动化配置平台：开发需求与实现说明

**文档版本：** 1.0（2026-11-12）  
**目标环境：** Windows、已安装并获许可的 STK 12、Python 3  
**交付定位：** 供 Codex 分阶段实施的工程规格；本文不是已实现功能说明。  
**首版边界：** 单机、本地文件、航空器与 TLE 卫星、多条双向通信链路、离线批量仿真。链路选择算法和 OMNeT++ 联动是后续模块。

## 1. 目标与硬约束

建立可复用的场景配置和数据生产平台：用户既可在 PySide6 GUI 中建立、编辑、保存和运行项目，也可用 CLI 或 Python API 调度同一项目。输入为航空器航迹（真实 CSV，或平台生成的模拟航迹）、**文件读取**的 TLE、收发机/天线/卫星及场景配置；STK 负责场景、轨道、几何与具备相应许可时的通信链路计算；平台输出规范化的三个 CSV 和运行清单，供后续预测、LDACS/卫星链路选择及网络仿真复用。

硬约束：

1. 航迹 CSV 和 TLE 均由文件选择器或路径参数读取。模拟航迹走生成器并保存为规范 CSV；不能把普通 CSV 当作 STK 原生航迹文件，须先转为 STK External Ephemeris `.e`。
2. TLE 只提供轨道要素；通信载荷、收发机、天线、姿态和业务参数从其他配置取得。TLE 文件解析成功不等于场景时间内传播可靠。
3. 上行 `Aircraft TX → Satellite RX` 与下行 `Satellite TX → Aircraft RX` 分别配置、分别计算、分别输出。设备按 ID 配对，不能用一套参数反向复用。
4. GUI 表单与 Python 调度读取同一配置模型和校验器。GUI 写出的文件必须能由 CLI 原样加载；CLI 修改的合规文件也必须能被 GUI 加载。
5. 所有输出使用 UTC 时间、明确单位与稳定 ID；缺乏计算依据时留空并给出状态，不以零填充，也不编造 BER 或链路余量。

## 2. 使用流程和页面规格

主窗口左侧为项目/页面导航，右侧为编辑区，底部为校验状态与日志摘要。顶部动作：**新建项目、打开项目目录或 `scenario.yaml`、保存、另存、验证、运行、取消**。显示项目根目录、配置版本、未保存标记、STK 连接状态。切换页面不丢失未保存数据；运行前将编辑状态落盘并通过全量校验。路径默认相对于项目根目录保存，外部绝对路径允许但在清单中标记不可移植。窗口关闭时提示未保存改动。

| 页面 | 控件与行为 | 校验和反馈 |
|---|---|---|
| 航迹输入 | `CSV 导入` / `模拟航迹` 两种来源；文件选择、首 N 行预览、时间/经纬度/高度/可选姿态字段映射、单位与坐标基准选择；模拟器输入起终点、UTC 起止、采样间隔、巡航高度、速度/插值方式，预览并导出规范 CSV | 时间可解析且严格递增、纬度 [-90,90]、经度 [-180,180]、高度单位明确、重复时刻/缺值提示；转换后的时间范围须覆盖场景时间，或明确采用交集并提示裁切 |
| TLE 卫星导入 | 选择 `.tle`/`.tce` 文件；解析卫星名称、NORAD/SSC 编号、历元、记录数、校验状态；搜索、过滤、勾选、批量选用；选中项生成/更新 `satellite_config.csv` | 成对行、编号一致、基础格式及校验和；重复编号、历元距离场景过远告警；文件不可读或选中卫星缺失阻断 |
| 场景参数 | UTC 起止、采样步长、最小仰角、坐标系、地球模型/传播选项、输出目录、轨迹来源、TLE 路径 | 起点早于终点；步长 >0；输出目录可写；所有影响数值的传播选项显式保存；未实现选项禁用 |
| 收发机 | 设备表：ID、平台类型/ID、TX/RX、频率、功率、带宽、数据率、噪声系数/系统温度、馈线损耗、极化、天线 ID；单独编辑上/下行链路配对及阈值 | 类型一致、频率/带宽/数据率正值、TX/RX 配对合法、引用存在；无物理意义的单元格置空/禁用；配置完整性按每条链路提示 |
| 天线 | 天线表：ID、归属、简化模型或外部方向图、峰值增益、中心频率、波束宽度、指向模式、安装方位/俯仰/横滚偏置、方向图文件；预览关联设备 | 外部方向图需文件和已实现的格式适配器；缺姿态却选择机体系固定指向时阻断或要求明确回退模型；极化/频率不匹配提示 |
| 规范文件导入/映射 | 插件选择、源文件、字段映射、单位转换预览、冲突策略、校验报告、导入到规范表；首版只列出确已实现的 CSV/YAML 适配器 | 未确认的设备/通信规范只显示“待实现适配器”，不假称可导入；适配器给出版本、格式、错误行号和源字段 |
| 仿真检查与运行 | 配置摘要、缺项/告警列表、校验报告导出、STK 版本/许可/连接检查、启动/附着方式、进度、结构化日志、取消按钮、失败诊断 | 阻断错误未清零不能运行；取消后状态为 `CANCELLED`；失败保留日志、阶段、错误码，不留下伪完整 CSV |
| 结果 | 三个 CSV 的相对/绝对路径、记录数、前 N 行预览、运行清单、打开输出目录 | 显示每文件是否完整、时间范围、可见/有效行数；部分失败明确标记为失败，禁止误报成功 |

表单的“加载”只解析为共同模型，按 schema 版本迁移/拒绝；“保存”先验证再原子写入（临时文件后替换）；“另存”复制所需输入文件并重写相对路径。导入原始文件与编辑规范文件是两条入口，最终收敛到同一模型。

## 3. 项目目录、配置与引用约定

```text
project/
├─ config/
│  ├─ scenario.yaml
│  ├─ transmitter_receiver.csv
│  ├─ antenna.csv
│  └─ satellite_config.csv
├─ input/
│  ├─ aircraft_track.csv       # CSV 来源或模拟器输出
│  └─ satellites.tle           # 用户提供的真实 TLE，不由平台伪造
├─ generated/                  # CSV→.e 中间文件
└─ runs/<run_id>/
   ├─ aircraft_state.csv
   ├─ link_geometry.csv
   ├─ link_budget.csv
   ├─ run_manifest.json
   ├─ validation_report.json
   └─ run.log
```

CSV：UTF-8（允许 BOM）、逗号分隔、首行为字段名、`.` 为小数点；无值写空单元格，不能写 `0`、`NaN`、`-9999` 代替缺失。ID 区分大小写，满足 `[A-Za-z][A-Za-z0-9_]*`，在各自实体类型内唯一。枚举使用下列英文常量。时间统一 ISO 8601 UTC，例如 `2026-11-12T02:00:00Z`；内部高精度可保留毫秒，输出精度统一且记录在清单。配置版本字段以 `schema_version: 1.0`（YAML）为权威；每张 CSV 加必填 `schema_version` 列、值 `1.0`，防止单独导入时版本不明。未知字段在 1.x 可保留并告警，未知必需枚举/新主版本拒绝。相对路径以 `project/` 为基准解析，不以当前工作目录解析。

### 3.1 `scenario.yaml` 完整示例

以下数值仅是**配置格式示例**，不代表已验证的射频设备或可用 TLE。运行时用真实 TLE 和相应场景时段替换。`tle_file` 必须是现有文件；模拟轨迹模式也需先生成 `aircraft_track.csv` 并记录生成参数。

```yaml
schema_version: '1.0'
project_id: DemoSatcom
scenario:
  start_utc: '2026-11-12T02:00:00Z'
  stop_utc: '2026-11-12T02:10:00Z'
  sample_step_s: 10
  time_scale: UTC
  earth_model: WGS84
  output_coordinate_frame: WGS84_GEODETIC
  min_elevation_deg: 5
inputs:
  aircraft_source: CSV             # CSV | GENERATED
  aircraft_track_file: input/aircraft_track.csv
  tle_file: input/satellites.tle
  transmitter_receiver_file: config/transmitter_receiver.csv
  antenna_file: config/antenna.csv
  satellite_config_file: config/satellite_config.csv
propagation:
  satellite_propagator: SGP4
  tle_max_age_days_warning: 14      # 告警阈值，非精度保证
  atmosphere_model: NONE            # 首版 NONE；扩展需实机验证
  rain_model: NONE
  polarization_loss_model: EXPLICIT # 从设备/链路参数取显式损耗
  default_other_loss_db: 0
attitude:
  aircraft_mode: UNAVAILABLE        # UNAVAILABLE | FROM_CSV | ASSUMED_LEVEL_TRACK
  satellite_mode: UNAVAILABLE       # 首版不得从 TLE 自动推断姿态
links:
  - link_id: U1
    direction: UPLINK
    tx_id: ATX1
    rx_id: SRX1
    min_cn_db: 3.0                 # 示例阈值；仅有阈值才算余量
    other_loss_db: 0
  - link_id: D1
    direction: DOWNLINK
    tx_id: STX1
    rx_id: ARX1
    min_cn_db: 3.0
    other_loss_db: 0
output:
  root_dir: runs
  retain_stk_scenario: true
  export_raw_reports: false
```

`scenario`、`inputs`、`propagation`、`attitude`、`links`、`output` 均必填。`start_utc`、`stop_utc`、`sample_step_s`、`time_scale=UTC`、`tle_file`、四个配置路径、`links`、`root_dir` 必填；`min_elevation_deg` 默认 0 但须写入保存结果；`*_model` 首版只接受已实现枚举。`aircraft_source=GENERATED` 时生成参数另存 `input/aircraft_generation.yaml`，运行时仍读取已生成规范 CSV，清单记录生成参数及哈希。`min_cn_db` 可空；为空时 `link_margin_db` 留空。未来可以增加 `min_ebn0_db`，但每条链路必须明确 `margin_basis`，避免混用阈值。

### 3.2 输入 CSV schema

| 文件/字段 | 类型与单位/枚举 | 必填 | 规则 |
|---|---|---|---|
| `aircraft_track.csv`: `schema_version`, `aircraft_id`, `time_utc`, `lat_deg`, `lon_deg`, `alt_m` | string, ID, UTC, deg, deg, m | 是 | 主键 `(aircraft_id,time_utc)`；首版坐标为 WGS84 大地经纬度，`alt_m` 为椭球高；非此高度基准须在导入映射时转换或拒绝 |
| 同上：`heading_deg`, `pitch_deg`, `roll_deg` | deg | 否 | 仅三列均有值且姿态定义/坐标约定在清单中明确时，`FROM_CSV` 可用；位置差分不自动视为可靠姿态 |
| `satellite_config.csv`: `schema_version`, `satellite_id`, `norad_id`, `display_name`, `enabled` | string, ID, integer, string, bool | 是 | `satellite_id` 主键；`norad_id` 必须存在于选定 TLE；`enabled` 为 `true`/`false`；每个启用编号唯一 |
| `transmitter_receiver.csv`: `schema_version`, `device_id`, `platform_type`, `platform_id`, `role`, `frequency_hz`, `power_dbw`, `bandwidth_hz`, `data_rate_bps`, `noise_figure_db`, `system_noise_temp_k`, `feeder_loss_db`, `polarization`, `antenna_id` | string, ID, `AIRCRAFT|SATELLITE`, ID, `TX|RX`, Hz, dBW, Hz, bit/s, dB, K, dB, `LINEAR_H|LINEAR_V|RHCP|LHCP`, ID | 条件必填 | `device_id` 主键；`platform_id` 引用航迹中的 `aircraft_id` 或卫星表 `satellite_id`；`antenna_id` 引用天线表。TX 必填 `power_dbw`,`data_rate_bps`，RX 必填噪声指标之一；频率/带宽/极化/馈线损耗均必填。对不适用字段留空，不能填 0 假装不适用 |
| `antenna.csv`: `schema_version`, `antenna_id`, `platform_type`, `platform_id`, `model`, `peak_gain_dbi`, `center_frequency_hz`, `beamwidth_deg`, `pointing_mode`, `mount_yaw_deg`, `mount_pitch_deg`, `mount_roll_deg`, `pattern_file` | string, ID, enum, ID, `SIMPLE|PATTERN_FILE`, dBi, Hz, deg, `ISOTROPIC|BORESIGHT_FIXED|TARGET_TRACKING`, deg×3, path | 条件必填 | `antenna_id` 主键。`SIMPLE` 必填增益与频率，方向性模型须波束宽度；`PATTERN_FILE` 必填文件且必须有实现的解析器；安装偏置缺省 0 需保存时显式写出。天线归属与设备归属一致 |

上表中功率采用 dBW；若 GUI 接收 dBm/W，保存前换算。`noise_figure_db` 与 `system_noise_temp_k` 至少有一项，若两者同时给出须定义优先级并在清单记录；首版建议只允许二选一。负的噪声系数、非正温度、负馈线损耗拒绝。频率匹配容差可配，默认 TX/RX 相对差 ≤ 0.1%；不同频段或带宽不一致给出明确错误/告警。`PATTERN_FILE` 的实际支持格式在适配器注册表中列出，首版可只实现 `SIMPLE` 并对 `PATTERN_FILE` 拒绝运行，不能静默退化为峰值增益。

规范 CSV 示例：

```csv
schema_version,aircraft_id,time_utc,lat_deg,lon_deg,alt_m,heading_deg,pitch_deg,roll_deg
1.0,AC1,2026-11-12T02:00:00Z,31.2304,121.4737,10000,,,
1.0,AC1,2026-11-12T02:00:10Z,31.2500,121.5000,10000,,,
```

```csv
schema_version,satellite_id,norad_id,display_name,enabled
1.0,SAT1,25544,ExampleSatellite,true
```

```csv
schema_version,device_id,platform_type,platform_id,role,frequency_hz,power_dbw,bandwidth_hz,data_rate_bps,noise_figure_db,system_noise_temp_k,feeder_loss_db,polarization,antenna_id
1.0,ATX1,AIRCRAFT,AC1,TX,14000000000,10,1000000,500000,,,1,RHCP,AANT_TX
1.0,ARX1,AIRCRAFT,AC1,RX,12000000000,,1000000,,3,,1,RHCP,AANT_RX
1.0,STX1,SATELLITE,SAT1,TX,12000000000,10,1000000,500000,,,1,RHCP,SANT_TX
1.0,SRX1,SATELLITE,SAT1,RX,14000000000,,1000000,,3,,1,RHCP,SANT_RX
```

```csv
schema_version,antenna_id,platform_type,platform_id,model,peak_gain_dbi,center_frequency_hz,beamwidth_deg,pointing_mode,mount_yaw_deg,mount_pitch_deg,mount_roll_deg,pattern_file
1.0,AANT_TX,AIRCRAFT,AC1,SIMPLE,15,14000000000,30,TARGET_TRACKING,0,0,0,
1.0,AANT_RX,AIRCRAFT,AC1,SIMPLE,15,12000000000,30,TARGET_TRACKING,0,0,0,
1.0,SANT_TX,SATELLITE,SAT1,SIMPLE,20,12000000000,20,TARGET_TRACKING,0,0,0,
1.0,SANT_RX,SATELLITE,SAT1,SIMPLE,20,14000000000,20,TARGET_TRACKING,0,0,0,
```

这里的 `TARGET_TRACKING` 是**显式理想跟踪假设**，不是从 TLE/航迹得到的真实姿态；输出和清单须标记。若研究需要机体系遮挡或真实方向图，应提供姿态时序与可验证的指向模型后再启用。

**TLE 文件约定：** 本地 UTF-8/ASCII 文本，允许“名称行 + 第 1/2 行”或纯成对第 1/2 行；使用 `.tle` 或 `.tce`；同一编号可含多历元，但具体选择策略必须记录。解析行号、卫星编号、历元、校验和；不得在示例项目中放入虚构可运行 TLE。示例中的 `25544` 仅是引用关系演示，实际文件必须包含该编号，且其历元与仿真时间相宜。运行禁止自动联网替换用户的 TLE。

## 4. 标准输出契约

所有 CSV 均写 UTF-8、固定表头、UTC 时间。时间网格 `t_i = start + i × step`，包含起点；若终点非步长整数倍，默认不额外插入终点，清单记录最后采样时刻。每个输出新增 `schema_version=1.0`。输出按 `(time_utc,aircraft_id,satellite_id,link_id)` 稳定排序。缺值空单元格；布尔值 `true|false`。状态字段与清单中的原因枚举一致。

### 4.1 `aircraft_state.csv`

主键 `(aircraft_id,time_utc)`；所有启用飞机 × 时间网格均有一行。位置缺失时保留行、`state_valid=false`，位置/姿态空，`invalid_reason=OUT_OF_COVERAGE|INTERPOLATION_FAILED|INPUT_INVALID`。插值方式首版为位置在 WGS84 固定系转换后线性插值，或直接使用 STK 采样结果，须固定一种并记录；不得跨越超出配置上限的轨迹空档静默插值。

| 字段 | 类型/单位 | 含义 |
|---|---|---|
| `schema_version`, `time_utc`, `aircraft_id` | string, UTC, ID | 版本、时间、飞机键 |
| `lat_deg`, `lon_deg`, `alt_m` | float, deg/deg/m | WGS84 大地位置，椭球高 |
| `heading_deg`, `pitch_deg`, `roll_deg` | float, deg | 有可信姿态来源时输出 |
| `state_valid`, `attitude_valid`, `attitude_source`, `invalid_reason` | bool, bool, enum, enum | 状态与依据；来源 `CSV|ASSUMED_LEVEL_TRACK|UNAVAILABLE` |

示例：

```csv
schema_version,time_utc,aircraft_id,lat_deg,lon_deg,alt_m,heading_deg,pitch_deg,roll_deg,state_valid,attitude_valid,attitude_source,invalid_reason
1.0,2026-11-12T02:00:00Z,AC1,31.2304,121.4737,10000,,,,true,false,UNAVAILABLE,
```

### 4.2 `link_geometry.csv`

主键 `(aircraft_id,satellite_id,time_utc)`；**所有启用飞机 × 启用卫星 × 时间点必须保留一行**，无论可见与否。仰角以航空器本地水平系定义；`visible` 由地球遮挡、仰角阈值和配置的 Access 约束决定。`range_m`、AER 等只在有效几何且按输出契约允许时填值；**不可见链路的几何量统一留空**，`geometry_valid=false`，避免后续误用。卫星传播失败也留空，原因不同。

| 字段 | 类型/单位 | 含义 |
|---|---|---|
| `schema_version`, `time_utc`, `aircraft_id`, `satellite_id` | string, UTC, ID, ID | 主键 |
| `visible`, `geometry_valid`, `visibility_reason` | bool, bool, enum | `VISIBLE|BELOW_ELEVATION|EARTH_BLOCKED|AIRCRAFT_STATE_INVALID|SATELLITE_STATE_INVALID|ACCESS_ERROR` |
| `range_m`, `azimuth_deg`, `elevation_deg`, `range_rate_mps` | float, m/deg/deg/m/s | 有效可见链路的几何采样；无法获取某个可选量时单独留空并在清单注明 |

示例（示意状态，数值须由实际运行计算）：

```csv
schema_version,time_utc,aircraft_id,satellite_id,visible,geometry_valid,visibility_reason,range_m,azimuth_deg,elevation_deg,range_rate_mps
1.0,2026-11-12T02:00:00Z,AC1,SAT1,false,false,BELOW_ELEVATION,,,,
```

### 4.3 `link_budget.csv`

主键 `(aircraft_id,satellite_id,time_utc,link_id)`；每条已配置链路 × 时间网格均有行，确保上下行及不可见时刻可关联。`direction` 必为 `UPLINK|DOWNLINK`；`tx_id`,`rx_id` 引用配置。`budget_valid=false` 时数值预算列留空，原因说明是不可见、缺姿态、模型不支持、计算失败等。`tx_gain_dbi` 与 `rx_gain_dbi` 是**在该时刻、该指向上的有效增益**，不是天线表峰值增益；理想跟踪假设须在 `assumption_flags` 标注。

| 字段 | 类型/单位 | 含义/计算前提 |
|---|---|---|
| `schema_version`, `time_utc`, `aircraft_id`, `satellite_id`, `link_id`, `direction`, `tx_id`, `rx_id` | string/UTC/ID/enum | 关联键 |
| `visible`, `budget_valid`, `invalid_reason`, `assumption_flags` | bool/bool/enum/string | `NOT_VISIBLE|GEOMETRY_INVALID|ATTITUDE_UNAVAILABLE|MODEL_UNSUPPORTED|STK_ERROR|MISSING_PARAMETER` 等；多个假设以 `;` 分隔 |
| `tx_power_dbw`, `tx_gain_dbi`, `eirp_dbw` | dBW/dBi/dBW | `EIRP = Tx 功率 - 发射馈线损耗 + 发射有效增益`；避免重复计入 STK 报告已含损耗 |
| `fspl_db`, `propagation_loss_db`, `other_loss_db`, `rx_gain_dbi` | dB/dB/dB/dBi | `propagation_loss_db` 不含 FSPL；损耗值为非负；传播模型/适用范围记录清单 |
| `received_power_dbw` | dBW | 按统一损耗口径，含接收馈线损耗；具体 STK 提供器映射须通过数值核对 |
| `bandwidth_hz`, `data_rate_bps`, `cn0_dbhz`, `cn_db`, `ebn0_db` | Hz/bit/s/dB-Hz/dB/dB | `C/N0` 需要有效噪声温度，`C/N` 需要带宽，`Eb/N0` 需要数据率；与 STK 报告相互校核 |
| `ber`, `link_margin_db`, `margin_basis` | 概率/dB/`CN|EBN0` | BER 仅在已配置且已验证调制编码/BER 曲线时输出；余量仅在对应阈值存在时输出 |

示例（不可见）：

```csv
schema_version,time_utc,aircraft_id,satellite_id,link_id,direction,tx_id,rx_id,visible,budget_valid,invalid_reason,assumption_flags,tx_power_dbw,tx_gain_dbi,eirp_dbw,fspl_db,propagation_loss_db,other_loss_db,rx_gain_dbi,received_power_dbw,bandwidth_hz,data_rate_bps,cn0_dbhz,cn_db,ebn0_db,ber,link_margin_db,margin_basis
1.0,2026-11-12T02:00:00Z,AC1,SAT1,U1,UPLINK,ATX1,SRX1,false,false,NOT_VISIBLE,,,,,,,,,,,,,,,,,
```

上述预算列是**物理层射频指标**。吞吐量、时延、抖动、丢包率、排队和切换中断属于 OMNeT++ 等网络层仿真输出；平台不得将 `data_rate_bps` 当作实测吞吐量，也不得由 `BER` 直接宣称网络丢包率。

## 5. STK 12 自动化边界与实现架构

优先在目标机器验证 **pywin32 或 comtypes + STK 12 COM/Connect**。STK 12.1 才引入新 STK Python API，因此不能把它作为 12.0 的前置条件。控制器封装 STK 版本探测、附着/启动、对象生命周期、单位设置、命令执行、Data Provider 读取和错误映射；不要在 GUI 页面直接拼接 Connect 命令。运行前检查 STK 安装、版本、相关许可（尤其 Communications）以及要用的数据提供器。无法满足时在预检阶段明确失败，不自动宣称可提供预算。

模块职责与数据流：

```text
GUI ─┐
CLI ─┼─> config loader → schema/semantic validator → RunPlan → orchestrator
API ─┘                                          ├─ trajectory adapter → .e
                                               ├─ TLE parser/import → SGP4 satellites
                                               ├─ STK Controller → objects/access/AER/Comm reports
                                               └─ normalizer → 3 CSV + manifest + log
```

1. **Python 配置/校验层：** 解析 YAML/CSV、版本、路径、外键、单位、时段；形成不可变 `ProjectConfig` 和 `RunPlan`。所有入口调用该层。
2. **轨迹适配器：** 校验真实 CSV 或模拟器生成的规范 CSV；按 STK `.e` 官方格式构造正确头、时间基准、坐标系、点数与数据行；首个可运行切片先做 STK round-trip：加载 `.e` 后读取若干位置，允许误差写入测试阈值。位置轨迹不能自动可靠恢复机体姿态；若无姿态，仅能使用 `ISOTROPIC` 或明确的 `TARGET_TRACKING` 理想模型，不得假装固定方向图已有正确指向。
3. **TLE 导入：** 本地文件解析与筛选，按编号导入 STK，使用 SGP4 传播并记录所用 TLE 历元、编号、传播时段、版本；处理同编号多历元与 STK 导入的重复对象。首版建议调用 STK 12 Connect `ImportTLEFile`，实机验证命令返回和对象命名。
4. **对象构建：** 创建 Aircraft、Satellite、TX/RX、Antenna，并显式建立上下行设备配对。支持 `SIMPLE` 的具体 STK 天线模型选择要在实现阶段通过 STK 12 验证并写入映射表；`PATTERN_FILE` 只在解析器与 STK 模型均验证后开放。
5. **几何：** STK 计算对象 Access、AER、距离等；Python 在统一时间网格上填全飞机-卫星组合，依 Access 区间/采样判定 `visible`，对可见样本读取几何值，对不可见样本留空。
6. **链路预算：** STK Communications/Access Data Provider 优先提供经验证的链路预算元素。Python 可以进行单位转换、统一表头、阈值余量计算和交叉核对；若 STK 无法提供某元素，可在明确物理模型/参数与来源后由 Python 计算并在清单标记 `computed_by=PYTHON`，不能静默拼凑或重复计损。BER 必须有调制/编码及 BER 模型，首版允许全列为空。损耗定义、噪声温度、极化和数据率口径要有单链路手算对照。
7. **导出：** 不直接把 STK 原始报告当标准 CSV。先收集报告和提供器结果，再由 normalizer 对齐 UTC 网格、外键、空值及状态并写标准输出；原始报告可选保留供追溯。

**需要固定并记录的假设：** WGS84 椭球高度、UTC 与 STK 时间转换、STK 对象单位偏好、航空器/卫星姿态来源、TLE 历元与传播区间、采样与插值规则、地球遮挡与最低仰角、发射/接收馈线损耗位置、有效天线增益的指向算法、传播损耗模型及各项许可。STK 所显示的名称/单位可能受版本和设置影响，适配器使用显式单位设置和字段映射，不以报告列序号硬编码。

## 6. 核心 API、CLI、日志和清单

建议公共接口（签名可微调，但职责和同源配置不可改变）：

```python
config = load_project(project_dir_or_scenario_yaml)  # -> ProjectConfig
report = validate_project(config, level="offline")  # 无 STK 的纯配置校验
report = validate_project(config, level="preflight") # 含 STK 版本/许可/能力
plan = build_run_plan(config)                          # 固定输入与时间网格
result = run_project(plan, progress=None, cancel_token=None)  # -> RunResult
```

CLI：

```powershell
python -m satcom_platform validate --project C:\path\to\project --offline --json
python -m satcom_platform validate --project C:\path\to\project --preflight
python -m satcom_platform run --project C:\path\to\project --output C:\path\to\project\runs\manual_run
python -m satcom_platform inspect --manifest C:\path\to\project\runs\manual_run\run_manifest.json
```

Python 调度：

```python
from satcom_platform import load_project, validate_project, build_run_plan, run_project

cfg = load_project(r"C:\path\to\project")
validation = validate_project(cfg, level="preflight")
validation.raise_for_errors()
result = run_project(build_run_plan(cfg))
print(result.manifest_path)
```

退出码：`0=SUCCESS`，`2=CONFIG_INVALID`，`3=INPUT_INVALID`，`4=STK_UNAVAILABLE_OR_UNSUPPORTED`，`5=STK_EXECUTION_FAILED`，`6=EXPORT_FAILED`，`7=CANCELLED`，`8=INTERNAL_ERROR`。日志每条含 UTC 时间、运行 ID、阶段、级别、错误码、实体 ID、简明消息、可选异常堆栈/建议操作；GUI 展示摘要，文件保存细节。记录输入路径及 SHA-256，不写系统凭据。阶段状态：`DRAFT → VALIDATING → READY → CONNECTING → BUILDING → COMPUTING → EXPORTING → SUCCEEDED`，任一运行阶段可转 `FAILED`/`CANCELLED`；状态持久化到清单。取消应先停止新任务，再清理本运行创建的 STK 对象，保留诊断资料。

`run_manifest.json` 至少包括：`manifest_version`、`run_id`、`project_id`、`status`、`started_utc`/`finished_utc`、`platform_version`、`python_version`、`stk_version`、`stk_license_capabilities`、`config_schema_version`、规范化配置快照或其路径/哈希、输入文件路径/大小/SHA-256、轨迹来源与生成参数、TLE 编号/历元与警告、时间网格、坐标/姿态/传播/天线假设、每个输出路径/行数/SHA-256、可见行数/有效预算行数、数据提供器映射与 `computed_by`、告警/错误列表、日志路径、结束原因。成功状态必须在三个 CSV 完整关闭并校验后才写入；输出采用临时文件与原子替换。

## 7. 工程结构与实施顺序

```text
satcom_platform/
├─ pyproject.toml
├─ src/satcom_platform/
│  ├─ config/{models,load_save,validate,migrate}.py
│  ├─ adapters/{track_csv,external_ephemeris,tle,import_registry}.py
│  ├─ simulation/{trajectory_generator,run_plan,orchestrator}.py
│  ├─ stk/{controller,objects,access,communications,providers}.py
│  ├─ output/{schemas,normalizer,manifest}.py
│  ├─ gui/{main_window,pages,workers}.py
│  ├─ cli.py
│  └─ __init__.py
├─ tests/{fixtures,unit,integration_stk,acceptance}/
├─ examples/minimal_project/       # 合法 TLE 由用户放入，不附虚构轨道数据
└─ docs/{setup,field_mapping,limitations}.md
```

**阶段 M0：环境探测。** 在目标 Windows 机器确认 STK 实际小版本、COM/Connect 可用性、Python 位数、Communications 许可、可访问的 Data Provider 及单位；形成 `docs/field_mapping.md` 与最小探针脚本。若只装 STK 12.0，不使用 12.1+ API。

**阶段 M1：纯 Python 配置核心。** 模型、schema、CSV/YAML 读写、路径与引用校验、模拟航迹生成、CLI `validate --offline`、规范示例项目；无 STK 可完整测试。先稳定配置格式，再制作 GUI。

**阶段 M2：STK 几何纵切。** CSV→`.e`、TLE 导入、飞机/卫星对象、时间网格、Access/AER、`aircraft_state.csv` 和完整 `link_geometry.csv`；给出 round-trip 与不可见样本测试。

**阶段 M3：上下行通信。** TX/RX/天线对象、上/下行独立配对、数据提供器映射、预算归一化与单链路数值核对、`link_budget.csv`。如 STK 能力缺失，停在预检并给出具体缺项，不虚报成功。

**阶段 M4：GUI。** 上述八页、同源配置模型、后台 worker、取消与结果预览；做 GUI 保存→CLI 加载、CLI 保存→GUI 加载的互通验收。

**阶段 M5：可靠性与文档。** 运行清单、原子导出、错误码、异常清理、样例/安装说明、回归验收。外部规范插件与方向图插件只先提供注册接口和示例适配器协议；实际格式得到样本与许可后再实现。

## 8. 验收清单与测试用例

最终每项须给出测试输入、预期、实际结果和对应日志/输出路径。数值误差阈值由 M0/M2 在目标 STK 12 环境建立基线并写入测试，不能凭空承诺“高精度”。

| 编号 | 场景 | 通过条件 |
|---|---|---|
| T01 | 无 STK 环境运行 `validate --offline` | 可加载规范项目、输出结构化错误/告警；不触发 STK；非法配置退出码 2/3 |
| T02 | STK 连接/版本/许可探测 | 记录实际版本与能力；不兼容/缺许可在预检失败，错误码 4 |
| T03 | TLE 本地导入 | 选中编号与导入对象一致；历元、文件哈希可追溯；重复/缺失编号有明确处理 |
| T04 | 轨迹 CSV→`.e` | STK 成功载入；抽样位置/时间与输入或指定插值结果误差在已记录阈值内；单位/高度基准正确 |
| T05 | 上下行预算 | 同一时刻分别输出 U1、D1；频率、功率、TX/RX ID 不串用；与 STK 原始报告/手算核对 |
| T06 | 不可见卫星 | `link_geometry` 的网格行不丢失，`visible=false`、几何空；预算行也在，预算量空 |
| T07 | 缺失姿态 | 固定波束需要姿态时阻断或标为无效；选择明确理想跟踪时清单与行级假设均有标记 |
| T08 | 时间同步 | UTC、边界、采样点、TLE/航迹覆盖和跨日输入正确；超覆盖范围显式无效/报错 |
| T09 | 重复 ID / 缺失引用 | 配置校验指出文件、行号、字段和被引用 ID；不启动 STK |
| T10 | 输出完整性 | 行数：state=`A×T`，geometry=`A×S×T`，budget=`Σ(每条链路对应飞机×卫星×T)`；主键唯一、外键存在、列/单位固定、清单哈希匹配 |
| T11 | GUI/CLI 同构 | GUI 保存后 CLI 校验/运行一致；CLI 加载的规范文件 GUI 可编辑再保存；没有隐式默认项丢失 |
| T12 | 取消与故障 | 中途取消/模拟提供器失败后状态和退出码准确；临时文件不被误认成功；可查看日志与诊断 |

**MVP 完成定义：** 使用一架飞机、一份用户提供的有效 TLE 至少一颗卫星、U1/D1 两条链路，在目标 STK 12 环境中从 GUI 与 CLI 均可运行；生成三个满足本契约的 CSV 和清单；重复运行可追溯输入与假设。若天线方向图或调制编码模型尚未实现，界面应禁用对应能力，预算 `ber` 留空，文档和运行清单明确限制。

## 9. 已核对的 STK 依据与实机核验点

- STK 官方说明：STK Python API 从 12.1 开始提供；旧版本使用 `win32com`/`comtypes`，因此本项目先走 COM/Connect。[STK Python 集成说明](https://help.agi.com/stk/12.7.0/Content/training/StartPython.htm)
- STK 12.0 Connect 提供 `ImportTLEFile`，支持从本地 TLE 文件按 SSC 编号导入、自动传播并设置步长/时段。[ImportTLEFile 命令](https://help.agi.com/stkdevkit/12.0.0/Subsystems/connectCmds/Content/cmd_ImportTLEFileSatellites.htm)
- STK 支持外部星历 `.e` 文件；文件头、坐标系和格式需按实际 STK 12 帮助与 round-trip 验证。[External Ephemeris 文件格式](https://help.agi.com/stk/content/stk/importfiles-02.htm)
- Access 数据提供器含 AER 与通信链路参数；BER 依赖调制/BER 曲线，不能从 Eb/N0 凭空输出。[Access Data Providers](https://help.agi.com/stkdevkit/12.0.0/Subsystems/dataProviders/Content/html/Access.htm)、[Comm Link Information](https://help.agi.com/stkdevkit/12.0.0/Subsystems/dataProviders/Content/html/dataProviders/Parameter_Set_Comm_Link_Information.htm)

**仍须实机确认：** 本机 STK 12 的小版本、安装方式与可用许可；Aircraft 外部星历的具体对象加载调用；可用天线模型、指向与姿态接口；每个链路预算元素的提供器路径、单位与损耗口径；取消执行时 STK 的响应行为。这些差异由 M0 探针和映射表固化，不应写成跨任意 STK 版本的兼容承诺。
