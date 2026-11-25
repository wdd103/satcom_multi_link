# M2 STK 几何与链路预算接入

网页“仿真检查与运行”现在会读取已保存的项目，启动本机 STK 12 COM，创建飞机与已启用卫星对象，并在“结果”页提供下载。运行状态由独立进程写入 `status.json`；任何 COM、导入或 Data Provider 错误都会标记为 `FAILED`，不会生成成功清单。

## 场景与数据

- 航迹 CSV 转为 STK `EphemerisLLATimePos` `.e`：UTC 场景历元、Earth Fixed、WGS84 大地坐标、高度米、Lagrange 一阶插值。导入后从 STK `LLA State/Fixed` 回读起止点和采样网格。
- 按卫星 CSV 中 `enabled=true` 的 NORAD ID 从配置的 TLE 文件导入，使用 STK SGP4 自动传播。多历元时，清单记录最接近场景起点的历元；导入的具体历元仍应以 STK 场景文件核对。
- 对每个飞机、卫星、时间组合计算 STK Access；可访问时从 `AER Data/Default` 读取方位角、仰角、距离。`access` 同时应用配置的最低仰角门限。无 Access 的行保留，几何值留空。
- `aircraft_state.csv`、`link_geometry.csv`、`link_budget.csv` 和 `manifest.json` 均位于一次运行的独立目录。`scenario.sc`、相关 STK sidecar 与 `.e` 文件打包为 `scenario_bundle.zip`。
- 对每条上下行链路，将配置中的卫星设备模板复制到所有已启用卫星，分别创建 STK Simple Transmitter/Receiver。发射端 `EIRP = 发射功率 + 发射天线峰值增益 − 发射馈线损耗 − 其他链路损耗`；接收端 `G/T = 接收天线峰值增益 − 接收馈线损耗 − 10log10(系统噪声温度)`。若仅配置噪声系数，则按 290 K 参考温度换算。频率和数据率写入 STK；从 `Link Information` 回读 C/N、Eb/No、BER，并核对带宽、EIRP 及 C/N 与 Eb/No 的关系。

## 实机核验

2026-11-15 使用本机 STK v12.6.0 与示例项目完成单星 `SAT41917` 的纵向运行：61 个采样点，61 行飞机状态，61 行几何结果，已生成 `.sc` 场景。该窗口内这颗卫星没有 Access，故所有几何行 `access=false`。

随后运行全部 80 颗已启用卫星，输出 `examples/minimal_project/runs/20261115T083013Z-78cf793d`：61 行飞机状态、4,880 行几何结果，109 行满足 5° 仰角门限，284 行由 STK 返回了可访问期间的方位角、仰角和距离。ZIP 包包含 80 个卫星 `.sa` 文件及输入快照，完整性检查通过。网页下载接口返回该包及 CSV。示例 TLE 距场景时刻约 30 天，因此这些结果用于验证接口和文件格式，不适合作为可信的轨道几何结论。

## 通信预算验证与边界

2026-11-15 在本机 STK 12.6 完成全部 80 颗已启用卫星的运行，目录为 `examples/minimal_project/runs/20261115T144039Z-e1bf92d3`。两条上下行链路分别生成 4,880 行预算，共 9,760 行，其中 218 行有链路访问；几何数据 4,880 行。场景包含 80 个卫星 `.sa` 文件、链路预算和设备/天线配置快照，ZIP 完整性检查通过。`SAT41918` 的一个上行采样回读 EIRP 24 dBW、G/T −8.624 dB/K、C/N −1.702 dB、Eb/No 1.309 dB、BER 0.0501。网页的预算 CSV 和场景包下载接口均返回 200。

此映射采用 STK Simple 模型。`TARGET_TRACKING` 按理想对准、恒定峰值增益处理；波束宽度与安装偏航/俯仰/滚转角尚未进入方向图或姿态计算。极化需匹配，但没有单独计算失配损耗；传播损耗按 STK 当前场景默认模型。示例 TLE 距场景时刻约 30 天，因此预算仅用于验证端到端映射和导出，不宜作为可信的链路设计结论。STK 保存的卫星 sidecar 可能保留源 TLE 的绝对路径；将压缩包迁移到另一台机器后需检查并重连该路径。

参考：[STK 外部星历格式](https://help.agi.com/stk/content/stk/importfiles-02.htm)、[STK 12 TLE 导入命令](https://help.agi.com/stkdevkit/12.0.0/Subsystems/connectCmds/Content/cmd_ImportTLEFileSatellites.htm)、[Simple Transmitter](https://help.agi.com/stkdevkit/12.0.0/Content/DocX/STKObjects~IAgTransmitterModelSimple.html)、[Simple Receiver](https://help.agi.com/stkdevkit/12.0.0/Content/DocX/STKObjects~IAgReceiverModelSimple.html)、[Link Information](https://help.agi.com/stkdevkit/12.0.0/Subsystems/dataProviders/Content/html/dataProviders/Link_Information~Access.htm)。
