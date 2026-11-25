# 示例输入

当前目录已包含本地 `satellites.tle` 和 `aircraft_track.csv`；具体记录以文件为准，不能把示例视为实时轨道或真实飞行数据。

- 航迹采用规范 CSV，可包含多架飞机；时间为 UTC，经纬度为度，高度为米。飞机 ID 必须与设备和场景配置一致。
- 卫星清单在 `../config/satellite_config.csv`。替换 TLE 后，应同步 NORAD 引用、启用选择与 `../config/scenario.yaml` 的场景时段；不要求固定包含 NORAD 25544。
- 示例 TLE 比当前示例场景早约 30 天，仅用于验证集成流程。
- 模型、原生模板和 `.bmsk` 在项目 `assets` 下；原始 `.sc` 导入来源不等于每次运行都依赖源场景文件。

使用步骤、数据口径和限制见[平台 README](../../../README.md)。
