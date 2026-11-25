stk.v.12.0
WrittenBy    STK_v12.6.0
BEGIN Scenario
    Name		 scenario_zhedang

    BEGIN Epoch

        Epoch		 12 Nov 2026 02:00:00.000000000
        SmartEpoch		
        BEGIN EVENT
            Epoch		 12 Nov 2026 02:00:00.000000000
            EventEpoch		
            BEGIN EVENT
                Type		 EVENT_LINKTO
                Name		 AnalysisStartTime
            END EVENT
            EpochState		 Implicit
        END EVENT


    END Epoch

    BEGIN Interval

        Start		 12 Nov 2026 02:00:00.000000000
        Stop		 12 Nov 2026 02:10:00.000000000
        SmartInterval		
        BEGIN EVENTINTERVAL
            StartEvent		
            BEGIN EVENT
                Epoch		 12 Nov 2026 02:00:00.000000000
                EpochState		 Explicit
            END EVENT
            StopEvent		
            BEGIN EVENT
                Epoch		 12 Nov 2026 02:10:00.000000000
                EpochState		 Explicit
            END EVENT
            IntervalState		 StartStop
        END EVENTINTERVAL

        EpochUsesAnalStart		 No
        AnimStartUsesAnalStart		 Yes
        AnimStopUsesAnalStop		 Yes

    END Interval

    BEGIN EOPFile

        InheritEOPSource		 No
        EOPFilename		 EOP-v1.1.txt

    END EOPFile

    BEGIN GlobalPrefs
        SatelliteNoOrbWarning		 No
        MissilePerigeeWarning		 No
        MissileStopTimeWarning		 No
        AircraftWGS84Warning		 Always
    END GlobalPrefs

    BEGIN CentralBody

        PrimaryBody		 Earth

    END CentralBody

    BEGIN CentralBodyTerrain

        BEGIN CentralBody
            Name		 Earth
            UseTerrainCache		 Yes
            TotalCacheSize		 402653184

            BEGIN StreamingTerrain
                UseCurrentStreamingTerrainServer		 Yes
                StreamingTerrainServerName		 assets.agi.com/stk-terrain/
                StreamingTerrainAzimuthElevationMaskEnabled		 No
                StreamingTerrainObscurationEnabled		 No
                StreamingTerrainCoverageGridObscurationEnabled		 No
            END StreamingTerrain
        END CentralBody

    END CentralBodyTerrain

    BEGIN StarCollection

        Name		 Hipparcos 2 Mag 8

    END StarCollection

    BEGIN ScenarioLicenses
        Module		 stk_mission_air
        Module		 stk_mission_level1
        Module		 stk_mission_level2
        Module		 stk_mission_level3
        Module		 stk_mission_space
        Module		 stk_propnav
        Module		 stk_snopt
    END ScenarioLicenses

    BEGIN Extensions

        BEGIN ClsApp
            RangeConstraint		 5000
            ApoPeriPad		 30000
            OrbitPathPad		 100000
            TimeDistPad		 30000
            OutOfDate		 2592000
            MaxApoPeriStep		 900
            ApoPeriAngle		 0.7853981633974483
            UseApogeePerigeeFilter		 Yes
            UsePathFilter		 No
            UseTimeFilter		 No
            UseOutOfDate		 Yes
            CreateSats		 No
            MaxSatsToCreate		 500
            UseModelScale		 No
            ModelScale		 0
            UseCrossRefDb		 Yes
            CollisionDB		 stkAllTLE.tce
            CollisionCrossRefDB		 stkAllTLE.sd
            ShowLine		 Yes
            AnimHighlight		 Yes
            StaticHighlight		 Yes
            UseLaunchWindow		 No
            LaunchWindowUseEntireTraj		 Yes
            LaunchWindowTrajMETStart		 0
            LaunchWindowTrajMETStop		 900
            LaunchWindowStart		 1130400
            LaunchWindowStop		 1216800
            LaunchMETOffset		 0
            LaunchWindowUseSecEphem		 No 
            LaunchWindowUseScenFolderForSecEphem		 Yes
            LaunchWindowUsePrimEphem		 No 
            LaunchWindowUseScenFolderForPrimEphem		 Yes
            LaunchWindowIntervalPtr		
            BEGIN EVENTINTERVAL
                BEGIN Interval
                    Start		 25 Nov 2026 04:00:00.000000000
                    Stop		 26 Nov 2026 04:00:00.000000000
                END Interval
                IntervalState		 Explicit
            END EVENTINTERVAL

            LaunchWindowUsePrimMTO		 No 
            GroupLaunches		 No 
            LWTimeConvergence		 0.001
            LWRelValueConvergence		 1e-08
            LWTSRTimeConvergence		 0.0001
            LWTSRRelValueConvergence		 1e-10
            LaunchWindowStep		 300
            MaxTSRStep		  1.8000000000000000e+02
            MaxTSRRelMotion		  2.0000000000000000e+01
            UseLaunchArea		 No 
            LaunchAreaOrientation		 North
            LaunchAreaAzimuth		 0
            LaunchAreaXLimits		 -10000 10000
            LaunchAreaYLimits		 -10000 10000
            LaunchAreaNumXIntrPnts		 1
            LaunchAreaNumYIntrPnts		 1
            LaunchAreaAltReference		 Ellipsoid
            TargetSameStop		 No 
            SkipSurfaceMetric		 No 
            LWAreaTSRRelValueConvergence		 1e-10
            AreaLaunchWindowStep		 300
            AreaMaxTSRStep		  3.0000000000000000e+01
            AreaMaxTSRRelMotion		 1
            ShowLaunchArea		 No 
            ShowBlackoutTracks		 No 
            ShowClearedTracks		 No 
            UseObjectForClearedColor		 No 
            BlackoutColor		 #ff0000
            ClearedColor		 #ffffff
            ShowTracksSegments		 No 
            ShowMinRangeTracks		 No 
            MinRangeTrackTimeStep		 0.5
            UsePrimStepForTracks		 Yes
            GfxTracksTimeStep		 30
            GfxAreaNumXIntrPnts		 1
            GfxAreaNumYIntrPnts		 1
            CreateLaunchMTO		 No 
            CovarianceSigmaScale		 3
            CovarianceMode		 None 
        END ClsApp

        BEGIN Units
            DistanceUnit		 Kilometers
            TimeUnit		 Seconds
            DateFormat		 GregorianUTC
            AngleUnit		 Degrees
            MassUnit		 Kilograms
            PowerUnit		 dBW
            FrequencyUnit		 Gigahertz
            SmallDistanceUnit		 Meters
            LatitudeUnit		 Degrees
            LongitudeUnit		 Degrees
            DurationUnit		 Hr:Min:Sec
            Temperature		 Kelvin
            SmallTimeUnit		 Seconds
            RatioUnit		 Decibel
            RcsUnit		 Decibel
            DopplerVelocityUnit		 MetersperSecond
            SARTimeResProdUnit		 Meter-Second
            ForceUnit		 Newtons
            PressureUnit		 Pascals
            SpecificImpulseUnit		 Seconds
            PRFUnit		 Kilohertz
            BandwidthUnit		 Megahertz
            SmallVelocityUnit		 CentimetersperSecond
            Percent		 Percentage
            AviatorDistanceUnit		 NauticalMiles
            AviatorTimeUnit		 Hours
            AviatorAltitudeUnit		 Feet
            AviatorFuelQuantityUnit		 Pounds
            AviatorRunwayLengthUnit		 Kilofeet
            AviatorBearingAngleUnit		 Degrees
            AviatorAngleOfAttackUnit		 Degrees
            AviatorAttitudeAngleUnit		 Degrees
            AviatorGUnit		 StandardSeaLevelG
            SolidAngle		 Steradians
            AviatorTSFCUnit		 TSFCLbmHrLbf
            AviatorPSFCUnit		 PSFCLbmHrHp
            AviatorForceUnit		 Pounds
            AviatorPowerUnit		 Horsepower
            SpectralBandwidthUnit		 Hertz
            AviatorAltTimeUnit		 Minutes
            AviatorSmallTimeUnit		 Seconds
            AviatorEnergyUnit		 kilowatt-hours
            BitsUnit		 MegaBits
            MagneticFieldUnit		 nanoTesla
            VoltageUnit		 Volts
        END Units

        BEGIN ReportUnits
            DistanceUnit		 Kilometers
            TimeUnit		 Seconds
            DateFormat		 GregorianUTC
            AngleUnit		 Degrees
            MassUnit		 Kilograms
            PowerUnit		 dBW
            FrequencyUnit		 Gigahertz
            SmallDistanceUnit		 Meters
            LatitudeUnit		 Degrees
            LongitudeUnit		 Degrees
            DurationUnit		 Hr:Min:Sec
            Temperature		 Kelvin
            SmallTimeUnit		 Seconds
            RatioUnit		 Decibel
            RcsUnit		 Decibel
            DopplerVelocityUnit		 MetersperSecond
            SARTimeResProdUnit		 Meter-Second
            ForceUnit		 Newtons
            PressureUnit		 Pascals
            SpecificImpulseUnit		 Seconds
            PRFUnit		 Kilohertz
            BandwidthUnit		 Megahertz
            SmallVelocityUnit		 CentimetersperSecond
            Percent		 Percentage
            AviatorDistanceUnit		 NauticalMiles
            AviatorTimeUnit		 Hours
            AviatorAltitudeUnit		 Feet
            AviatorFuelQuantityUnit		 Pounds
            AviatorRunwayLengthUnit		 Kilofeet
            AviatorBearingAngleUnit		 Degrees
            AviatorAngleOfAttackUnit		 Degrees
            AviatorAttitudeAngleUnit		 Degrees
            AviatorGUnit		 StandardSeaLevelG
            SolidAngle		 Steradians
            AviatorTSFCUnit		 TSFCLbmHrLbf
            AviatorPSFCUnit		 PSFCLbmHrHp
            AviatorForceUnit		 Pounds
            AviatorPowerUnit		 Horsepower
            SpectralBandwidthUnit		 Hertz
            AviatorAltTimeUnit		 Minutes
            AviatorSmallTimeUnit		 Seconds
            AviatorEnergyUnit		 kilowatt-hours
            BitsUnit		 MegaBits
            MagneticFieldUnit		 nanoTesla
            VoltageUnit		 Volts
        END ReportUnits

        BEGIN ConnectReportUnits
            DistanceUnit		 Kilometers
            TimeUnit		 Seconds
            DateFormat		 GregorianUTC
            AngleUnit		 Degrees
            MassUnit		 Kilograms
            PowerUnit		 dBW
            FrequencyUnit		 Gigahertz
            SmallDistanceUnit		 Meters
            LatitudeUnit		 Degrees
            LongitudeUnit		 Degrees
            DurationUnit		 Hr:Min:Sec
            Temperature		 Kelvin
            SmallTimeUnit		 Seconds
            RatioUnit		 Decibel
            RcsUnit		 Decibel
            DopplerVelocityUnit		 MetersperSecond
            SARTimeResProdUnit		 Meter-Second
            ForceUnit		 Newtons
            PressureUnit		 Pascals
            SpecificImpulseUnit		 Seconds
            PRFUnit		 Kilohertz
            BandwidthUnit		 Megahertz
            SmallVelocityUnit		 CentimetersperSecond
            Percent		 Percentage
            AviatorDistanceUnit		 NauticalMiles
            AviatorTimeUnit		 Hours
            AviatorAltitudeUnit		 Feet
            AviatorFuelQuantityUnit		 Pounds
            AviatorRunwayLengthUnit		 Kilofeet
            AviatorBearingAngleUnit		 Degrees
            AviatorAngleOfAttackUnit		 Degrees
            AviatorAttitudeAngleUnit		 Degrees
            AviatorGUnit		 StandardSeaLevelG
            SolidAngle		 Steradians
            AviatorTSFCUnit		 TSFCLbmHrLbf
            AviatorPSFCUnit		 PSFCLbmHrHp
            AviatorForceUnit		 Pounds
            AviatorPowerUnit		 Horsepower
            SpectralBandwidthUnit		 Hertz
            AviatorAltTimeUnit		 Minutes
            AviatorSmallTimeUnit		 Seconds
            AviatorEnergyUnit		 kilowatt-hours
            BitsUnit		 MegaBits
            MagneticFieldUnit		 nanoTesla
            VoltageUnit		 Volts
        END ConnectReportUnits

        BEGIN ReportFavorites
        END ReportFavorites

        BEGIN ADFFileData
        END ADFFileData

        BEGIN GenDb

            BEGIN Database
                DbType		 Satellite
                DefDb		 stkAllTLE.sd
                UseMyDb		 Off
                MaxMatches		 2000
                Use4SOC		 On

                BEGIN FieldDefaults

                    BEGIN Field
                        Name		 "SSC Number"
                        Default		 "*"
                    END Field

                    BEGIN Field
                        Name		 "Common Name"
                        Default		 "*"
                    END Field

                END FieldDefaults

            END Database

            BEGIN Database
                DbType		 City
                DefDb		 stkCityDb.cd
                UseMyDb		 Off
                MaxMatches		 2000
                Use4SOC		 On

                BEGIN FieldDefaults

                    BEGIN Field
                        Name		 "City Name"
                        Default		 "*"
                    END Field

                END FieldDefaults

            END Database

            BEGIN Database
                DbType		 Facility
                DefDb		 stkFacility.fd
                UseMyDb		 Off
                MaxMatches		 2000
                Use4SOC		 On

                BEGIN FieldDefaults

                END FieldDefaults

            END Database
        END GenDb

        BEGIN SOCDb
            BEGIN Defaults
            END Defaults
        END SOCDb

        BEGIN Msgp4Ext
        END Msgp4Ext

        BEGIN FileLocations
        END FileLocations

        BEGIN Author
            Optimize		 No
            UseBasicGlobe		 No
            SaveEphemeris		 Yes
            SaveScenFolder		 No
            BEGIN ExternalFileTypes
                BEGIN Type
                    FileType		 Calculation Scalar
                    Include		 Yes
                END Type
                BEGIN Type
                    FileType		 Celestial Image
                    Include		 No
                END Type
                BEGIN Type
                    FileType		 Cloud
                    Include		 Yes
                END Type
                BEGIN Type
                    FileType		 Component Supporting File
                    Include		 Yes
                END Type
                BEGIN Type
                    FileType		 EOIR Texture Map File
                    Include		 Yes
                END Type
                BEGIN Type
                    FileType		 EOP
                    Include		 Yes
                END Type
                BEGIN Type
                    FileType		 External Vector Data
                    Include		 Yes
                END Type
                BEGIN Type
                    FileType		 Globe
                    Include		 Yes
                END Type
                BEGIN Type
                    FileType		 Globe Data
                    Include		 No
                END Type
                BEGIN Type
                    FileType		 Map
                    Include		 No
                END Type
                BEGIN Type
                    FileType		 Map Image
                    Include		 No
                END Type
                BEGIN Type
                    FileType		 Marker/Label
                    Include		 Yes
                END Type
                BEGIN Type
                    FileType		 Model
                    Include		 Yes
                END Type
                BEGIN Type
                    FileType		 Object Break-up File
                    Include		 No
                END Type
                BEGIN Type
                    FileType		 Planetary Ephemeris
                    Include		 No
                END Type
                BEGIN Type
                    FileType		 Python Script
                    Include		 Yes
                END Type
                BEGIN Type
                    FileType		 Report Style Script
                    Include		 Yes
                END Type
                BEGIN Type
                    FileType		 Report/Graph Style
                    Include		 Yes
                END Type
                BEGIN Type
                    FileType		 Scalar Calculation File
                    Include		 Yes
                END Type
                BEGIN Type
                    FileType		 Terrain
                    Include		 Yes
                END Type
                BEGIN Type
                    FileType		 Volume Grid Intervals File
                    Include		 Yes
                END Type
                BEGIN Type
                    FileType		 Volumetric File
                    Include		 Yes
                END Type
                BEGIN Type
                    FileType		 WTM
                    Include		 Yes
                END Type
            END ExternalFileTypes
            ReadOnly		 No
            ViewerPassword		 No
            STKPassword		 No
            ExcludeInstallFiles		 No
            BEGIN ExternalFileList
            END ExternalFileList
        END Author

        BEGIN ExportDataFile
            FileType		 Ephemeris
            IntervalType		 Ephemeris
            TimePeriodStart		 0
            TimePeriodStop		 0
            StepType		 Ephemeris
            StepSize		 60
            EphemType		 STK
            UseVehicleCentralBody		 Yes
            CentralBody		 Earth
            SatelliteID		 -200000
            CoordSys		 ICRF
            NonSatCoordSys		 Fixed
            InterpolateBoundaries		 Yes
            EphemFormat		 Current
            InterpType		 9
            InterpOrder		 5
            AttCoordSys		 Fixed
            Quaternions		 0
            ExportCovar		 Position
            AttitudeFormat		 Current
            TimePrecision		 6
            CCSDSDateFormat		 YMD
            CCSDSEphFormat		 SciNotation
            CCSDSTimeSystem		 UTC
            CCSDSRefFrame		 ICRF
            UseSatCenterAndFrame		 No
            IncludeCovariance		 No
            IncludeAcceleration		 No
            CCSDSFileFormat		 KVN
        END ExportDataFile

        BEGIN Desc
        END Desc

        BEGIN RfEnv
<?xml version = "1.0" standalone = "yes"?>
<SCOPE>
    <VAR name = "PropagationChannel">
        <SCOPE>
            <VAR name = "UseITU618Section2p5">
                <BOOL>false</BOOL>
            </VAR>
            <VAR name = "UseCloudFogModel">
                <BOOL>true</BOOL>
            </VAR>
            <VAR name = "CloudFogModel">
                <VAR name = "ITU-R_P840-7">
                    <SCOPE Class = "LinkEmbedControl">
                        <VAR name = "ReferenceType">
                            <STRING>&quot;Unlinked&quot;</STRING>
                        </VAR>
                        <VAR name = "Component">
                            <VAR name = "ITU-R_P840-7">
                                <SCOPE Class = "CloudFogLossModel">
                                    <VAR name = "Version">
                                        <STRING>&quot;1.0.0 a&quot;</STRING>
                                    </VAR>
                                    <VAR name = "IdentifierInformation">
                                        <SCOPE>
                                            <VAR name = "Identifier">
                                                <STRING>&quot;{EE1C07D8-5044-40DF-BE91-80B82C44BD4F}&quot;</STRING>
                                            </VAR>
                                            <VAR name = "Version">
                                                <STRING>&quot;5&quot;</STRING>
                                            </VAR>
                                            <VAR name = "SdfInformation">
                                                <SCOPE>
                                                    <VAR name = "Version">
                                                        <STRING>&quot;0.0&quot;</STRING>
                                                    </VAR>
                                                    <VAR name = "Url">
                                                        <STRING>&quot;&quot;</STRING>
                                                    </VAR>
                                                </SCOPE>
                                            </VAR>
                                            <VAR name = "SourceIdentifierInformation">
                                                <SCOPE>
                                                    <VAR name = "Identifier">
                                                        <STRING>&quot;{E7BA4392-37BE-4446-A5C7-6068165B166A}&quot;</STRING>
                                                    </VAR>
                                                    <VAR name = "Version">
                                                        <STRING>&quot;1&quot;</STRING>
                                                    </VAR>
                                                    <VAR name = "SdfInformation">
                                                        <SCOPE>
                                                            <VAR name = "Version">
                                                                <STRING>&quot;0.0&quot;</STRING>
                                                            </VAR>
                                                            <VAR name = "Url">
                                                                <STRING>&quot;&quot;</STRING>
                                                            </VAR>
                                                        </SCOPE>
                                                    </VAR>
                                                </SCOPE>
                                            </VAR>
                                        </SCOPE>
                                    </VAR>
                                    <VAR name = "ComponentName">
                                        <STRING>&quot;ITU-R_P840-7&quot;</STRING>
                                    </VAR>
                                    <VAR name = "Description">
                                        <STRING>&quot;ITU-R P840-7&quot;</STRING>
                                    </VAR>
                                    <VAR name = "Type">
                                        <STRING>&quot;ITU-R P840-7&quot;</STRING>
                                    </VAR>
                                    <VAR name = "UserComment">
                                        <STRING>&quot;ITU-R P840-7&quot;</STRING>
                                    </VAR>
                                    <VAR name = "ReadOnly">
                                        <BOOL>false</BOOL>
                                    </VAR>
                                    <VAR name = "Clonable">
                                        <BOOL>true</BOOL>
                                    </VAR>
                                    <VAR name = "Category">
                                        <STRING>&quot;@Top&quot;</STRING>
                                    </VAR>
                                    <VAR name = "LiquidWaterDensityValueChoice">
                                        <STRING>&quot;Liquid Water Content Density Value&quot;</STRING>
                                    </VAR>
                                    <VAR name = "CloudCeiling">
                                        <QUANTITY Dimension = "DistanceUnit" Unit = "m">
                                            <REAL>3000</REAL>
                                        </QUANTITY>
                                    </VAR>
                                    <VAR name = "CloudLayerThickness">
                                        <QUANTITY Dimension = "DistanceUnit" Unit = "m">
                                            <REAL>500</REAL>
                                        </QUANTITY>
                                    </VAR>
                                    <VAR name = "CloudTemp">
                                        <QUANTITY Dimension = "Temperature" Unit = "K">
                                            <REAL>273.15</REAL>
                                        </QUANTITY>
                                    </VAR>
                                    <VAR name = "CloudLiqWaterDensity">
                                        <QUANTITY Dimension = "SmallDensity" Unit = "kg*m^-3">
                                            <REAL>0.0005</REAL>
                                        </QUANTITY>
                                    </VAR>
                                    <VAR name = "AnnualAveragePercentValue">
                                        <QUANTITY Dimension = "Percent" Unit = "unitValue">
                                            <REAL>0.01</REAL>
                                        </QUANTITY>
                                    </VAR>
                                    <VAR name = "MonthlyAveragePercentValue">
                                        <QUANTITY Dimension = "Percent" Unit = "unitValue">
                                            <REAL>0.01</REAL>
                                        </QUANTITY>
                                    </VAR>
                                    <VAR name = "LiqWaterAverageDataMonth">
                                        <INT>1</INT>
                                    </VAR>
                                    <VAR name = "UseRainHeightAsCloudThickness">
                                        <BOOL>false</BOOL>
                                    </VAR>
                                </SCOPE>
                            </VAR>
                        </VAR>
                    </SCOPE>
                </VAR>
            </VAR>
            <VAR name = "UseTropoScintModel">
                <BOOL>true</BOOL>
            </VAR>
            <VAR name = "TropoScintModel">
                <VAR name = "ITU-R_P618-12">
                    <SCOPE Class = "LinkEmbedControl">
                        <VAR name = "ReferenceType">
                            <STRING>&quot;Unlinked&quot;</STRING>
                        </VAR>
                        <VAR name = "Component">
                            <VAR name = "ITU-R_P618-12">
                                <SCOPE Class = "TropoScintLossModel">
                                    <VAR name = "Version">
                                        <STRING>&quot;1.0.0 a&quot;</STRING>
                                    </VAR>
                                    <VAR name = "IdentifierInformation">
                                        <SCOPE>
                                            <VAR name = "Identifier">
                                                <STRING>&quot;{A6EDAA1F-850C-47B0-B1EF-B8BB88C44947}&quot;</STRING>
                                            </VAR>
                                            <VAR name = "Version">
                                                <STRING>&quot;2&quot;</STRING>
                                            </VAR>
                                            <VAR name = "SdfInformation">
                                                <SCOPE>
                                                    <VAR name = "Version">
                                                        <STRING>&quot;0.0&quot;</STRING>
                                                    </VAR>
                                                    <VAR name = "Url">
                                                        <STRING>&quot;&quot;</STRING>
                                                    </VAR>
                                                </SCOPE>
                                            </VAR>
                                            <VAR name = "SourceIdentifierInformation">
                                                <SCOPE>
                                                    <VAR name = "Identifier">
                                                        <STRING>&quot;{BC27045B-5A54-458E-BF17-702BCFE40CA8}&quot;</STRING>
                                                    </VAR>
                                                    <VAR name = "Version">
                                                        <STRING>&quot;1&quot;</STRING>
                                                    </VAR>
                                                    <VAR name = "SdfInformation">
                                                        <SCOPE>
                                                            <VAR name = "Version">
                                                                <STRING>&quot;0.0&quot;</STRING>
                                                            </VAR>
                                                            <VAR name = "Url">
                                                                <STRING>&quot;&quot;</STRING>
                                                            </VAR>
                                                        </SCOPE>
                                                    </VAR>
                                                </SCOPE>
                                            </VAR>
                                        </SCOPE>
                                    </VAR>
                                    <VAR name = "ComponentName">
                                        <STRING>&quot;ITU-R_P618-12&quot;</STRING>
                                    </VAR>
                                    <VAR name = "Description">
                                        <STRING>&quot;ITU-R P618-12&quot;</STRING>
                                    </VAR>
                                    <VAR name = "Type">
                                        <STRING>&quot;ITU-R P618-12&quot;</STRING>
                                    </VAR>
                                    <VAR name = "UserComment">
                                        <STRING>&quot;ITU-R P618-12&quot;</STRING>
                                    </VAR>
                                    <VAR name = "ReadOnly">
                                        <BOOL>false</BOOL>
                                    </VAR>
                                    <VAR name = "Clonable">
                                        <BOOL>true</BOOL>
                                    </VAR>
                                    <VAR name = "Category">
                                        <STRING>&quot;@Top&quot;</STRING>
                                    </VAR>
                                    <VAR name = "FadeDepthAverageTimeChoice">
                                        <STRING>&quot;Fade depth for the average year&quot;</STRING>
                                    </VAR>
                                    <VAR name = "FadeExceeded">
                                        <QUANTITY Dimension = "Percent" Unit = "unitValue">
                                            <REAL>0.001</REAL>
                                        </QUANTITY>
                                    </VAR>
                                    <VAR name = "PercentTimeRefracGrad">
                                        <QUANTITY Dimension = "Percent" Unit = "unitValue">
                                            <REAL>0.1</REAL>
                                        </QUANTITY>
                                    </VAR>
                                    <VAR name = "SurfaceTemperature">
                                        <QUANTITY Dimension = "Temperature" Unit = "K">
                                            <REAL>273.15</REAL>
                                        </QUANTITY>
                                    </VAR>
                                </SCOPE>
                            </VAR>
                        </VAR>
                    </SCOPE>
                </VAR>
            </VAR>
            <VAR name = "UseIonoFadingModel">
                <BOOL>false</BOOL>
            </VAR>
            <VAR name = "IonoFadingModel">
                <VAR name = "ITU-R_P531-13">
                    <SCOPE Class = "LinkEmbedControl">
                        <VAR name = "ReferenceType">
                            <STRING>&quot;Unlinked&quot;</STRING>
                        </VAR>
                        <VAR name = "Component">
                            <VAR name = "ITU-R_P531-13">
                                <SCOPE Class = "IonoFadingLossModel">
                                    <VAR name = "Version">
                                        <STRING>&quot;1.0.0 a&quot;</STRING>
                                    </VAR>
                                    <VAR name = "IdentifierInformation">
                                        <SCOPE>
                                            <VAR name = "Identifier">
                                                <STRING>&quot;{82B03995-D71D-473B-A2D2-8E611A6A4F1F}&quot;</STRING>
                                            </VAR>
                                            <VAR name = "Version">
                                                <STRING>&quot;1&quot;</STRING>
                                            </VAR>
                                            <VAR name = "SdfInformation">
                                                <SCOPE>
                                                    <VAR name = "Version">
                                                        <STRING>&quot;0.0&quot;</STRING>
                                                    </VAR>
                                                    <VAR name = "Url">
                                                        <STRING>&quot;&quot;</STRING>
                                                    </VAR>
                                                </SCOPE>
                                            </VAR>
                                            <VAR name = "SourceIdentifierInformation">
                                                <SCOPE>
                                                    <VAR name = "Identifier">
                                                        <STRING>&quot;{1699891E-9828-41C7-ADD4-4BE20EFC34A8}&quot;</STRING>
                                                    </VAR>
                                                    <VAR name = "Version">
                                                        <STRING>&quot;1&quot;</STRING>
                                                    </VAR>
                                                    <VAR name = "SdfInformation">
                                                        <SCOPE>
                                                            <VAR name = "Version">
                                                                <STRING>&quot;0.0&quot;</STRING>
                                                            </VAR>
                                                            <VAR name = "Url">
                                                                <STRING>&quot;&quot;</STRING>
                                                            </VAR>
                                                        </SCOPE>
                                                    </VAR>
                                                </SCOPE>
                                            </VAR>
                                        </SCOPE>
                                    </VAR>
                                    <VAR name = "ComponentName">
                                        <STRING>&quot;ITU-R_P531-13&quot;</STRING>
                                    </VAR>
                                    <VAR name = "Description">
                                        <STRING>&quot;ITU-R P531-13&quot;</STRING>
                                    </VAR>
                                    <VAR name = "Type">
                                        <STRING>&quot;ITU-R P531-13&quot;</STRING>
                                    </VAR>
                                    <VAR name = "UserComment">
                                        <STRING>&quot;ITU-R P531-13&quot;</STRING>
                                    </VAR>
                                    <VAR name = "ReadOnly">
                                        <BOOL>false</BOOL>
                                    </VAR>
                                    <VAR name = "Clonable">
                                        <BOOL>true</BOOL>
                                    </VAR>
                                    <VAR name = "Category">
                                        <STRING>&quot;@Top&quot;</STRING>
                                    </VAR>
                                    <VAR name = "UseAlternateAPFile">
                                        <BOOL>false</BOOL>
                                    </VAR>
                                    <VAR name = "AlternateAPDataFile">
                                        <STRING>
                                            <PROP name = "FullName">
                                                <STRING>&quot;&quot;</STRING>
                                            </PROP>&quot;&quot;</STRING>
                                    </VAR>
                                </SCOPE>
                            </VAR>
                        </VAR>
                    </SCOPE>
                </VAR>
            </VAR>
            <VAR name = "UseRainModel">
                <BOOL>true</BOOL>
            </VAR>
            <VAR name = "RainModel">
                <VAR name = "ITU-R_P618-13">
                    <SCOPE Class = "LinkEmbedControl">
                        <VAR name = "ReferenceType">
                            <STRING>&quot;Unlinked&quot;</STRING>
                        </VAR>
                        <VAR name = "Component">
                            <VAR name = "ITU-R_P618-13">
                                <SCOPE Class = "RainLossModel">
                                    <VAR name = "Version">
                                        <STRING>&quot;1.0.0 a&quot;</STRING>
                                    </VAR>
                                    <VAR name = "IdentifierInformation">
                                        <SCOPE>
                                            <VAR name = "Identifier">
                                                <STRING>&quot;{E3B4A3E5-CE49-47EF-87FC-2345793D508C}&quot;</STRING>
                                            </VAR>
                                            <VAR name = "Version">
                                                <STRING>&quot;1&quot;</STRING>
                                            </VAR>
                                            <VAR name = "SdfInformation">
                                                <SCOPE>
                                                    <VAR name = "Version">
                                                        <STRING>&quot;0.0&quot;</STRING>
                                                    </VAR>
                                                    <VAR name = "Url">
                                                        <STRING>&quot;&quot;</STRING>
                                                    </VAR>
                                                </SCOPE>
                                            </VAR>
                                            <VAR name = "SourceIdentifierInformation">
                                                <SCOPE>
                                                    <VAR name = "Identifier">
                                                        <STRING>&quot;{62382EA0-41C0-45F7-AA94-ACC684509D66}&quot;</STRING>
                                                    </VAR>
                                                    <VAR name = "Version">
                                                        <STRING>&quot;1&quot;</STRING>
                                                    </VAR>
                                                    <VAR name = "SdfInformation">
                                                        <SCOPE>
                                                            <VAR name = "Version">
                                                                <STRING>&quot;0.0&quot;</STRING>
                                                            </VAR>
                                                            <VAR name = "Url">
                                                                <STRING>&quot;&quot;</STRING>
                                                            </VAR>
                                                        </SCOPE>
                                                    </VAR>
                                                </SCOPE>
                                            </VAR>
                                        </SCOPE>
                                    </VAR>
                                    <VAR name = "ComponentName">
                                        <STRING>&quot;ITU-R_P618-13&quot;</STRING>
                                    </VAR>
                                    <VAR name = "Description">
                                        <STRING>&quot;ITU-R P618-13 rain model&quot;</STRING>
                                    </VAR>
                                    <VAR name = "Type">
                                        <STRING>&quot;ITU-R P618-13&quot;</STRING>
                                    </VAR>
                                    <VAR name = "UserComment">
                                        <STRING>&quot;ITU-R P618-13 rain model&quot;</STRING>
                                    </VAR>
                                    <VAR name = "ReadOnly">
                                        <BOOL>false</BOOL>
                                    </VAR>
                                    <VAR name = "Clonable">
                                        <BOOL>true</BOOL>
                                    </VAR>
                                    <VAR name = "Category">
                                        <STRING>&quot;@Top&quot;</STRING>
                                    </VAR>
                                    <VAR name = "SurfaceTemperature">
                                        <QUANTITY Dimension = "Temperature" Unit = "K">
                                            <REAL>273.15</REAL>
                                        </QUANTITY>
                                    </VAR>
                                    <VAR name = "EnableDepolarizationLoss">
                                        <BOOL>false</BOOL>
                                    </VAR>
                                    <VAR name = "EnableITU1510">
                                        <BOOL>false</BOOL>
                                    </VAR>
                                    <VAR name = "UseAnnualITU1510">
                                        <BOOL>true</BOOL>
                                    </VAR>
                                    <VAR name = "ITU1510Month">
                                        <STRING>&quot;January&quot;</STRING>
                                    </VAR>
                                </SCOPE>
                            </VAR>
                        </VAR>
                    </SCOPE>
                </VAR>
            </VAR>
            <VAR name = "UseAtmosAbsorptionModel">
                <BOOL>true</BOOL>
            </VAR>
            <VAR name = "AtmosAbsorptionModel">
                <VAR name = "ITU-R_P676-9">
                    <SCOPE Class = "LinkEmbedControl">
                        <VAR name = "ReferenceType">
                            <STRING>&quot;Unlinked&quot;</STRING>
                        </VAR>
                        <VAR name = "Component">
                            <VAR name = "ITU-R_P676-9">
                                <SCOPE Class = "AtmosphericAbsorptionModel">
                                    <VAR name = "Version">
                                        <STRING>&quot;1.0.1 a&quot;</STRING>
                                    </VAR>
                                    <VAR name = "IdentifierInformation">
                                        <SCOPE>
                                            <VAR name = "Identifier">
                                                <STRING>&quot;{7AD3F99F-E9BD-4879-8A50-04EEF1A35854}&quot;</STRING>
                                            </VAR>
                                            <VAR name = "Version">
                                                <STRING>&quot;1&quot;</STRING>
                                            </VAR>
                                            <VAR name = "SdfInformation">
                                                <SCOPE>
                                                    <VAR name = "Version">
                                                        <STRING>&quot;0.0&quot;</STRING>
                                                    </VAR>
                                                    <VAR name = "Url">
                                                        <STRING>&quot;&quot;</STRING>
                                                    </VAR>
                                                </SCOPE>
                                            </VAR>
                                            <VAR name = "SourceIdentifierInformation">
                                                <SCOPE>
                                                    <VAR name = "Identifier">
                                                        <STRING>&quot;{5DBDF434-D4CA-44F6-8097-A6EBF681200D}&quot;</STRING>
                                                    </VAR>
                                                    <VAR name = "Version">
                                                        <STRING>&quot;1&quot;</STRING>
                                                    </VAR>
                                                    <VAR name = "SdfInformation">
                                                        <SCOPE>
                                                            <VAR name = "Version">
                                                                <STRING>&quot;0.0&quot;</STRING>
                                                            </VAR>
                                                            <VAR name = "Url">
                                                                <STRING>&quot;&quot;</STRING>
                                                            </VAR>
                                                        </SCOPE>
                                                    </VAR>
                                                </SCOPE>
                                            </VAR>
                                        </SCOPE>
                                    </VAR>
                                    <VAR name = "ComponentName">
                                        <STRING>&quot;ITU-R_P676-9&quot;</STRING>
                                    </VAR>
                                    <VAR name = "Description">
                                        <STRING>&quot;ITU-R P676-9 gaseous absorption model&quot;</STRING>
                                    </VAR>
                                    <VAR name = "Type">
                                        <STRING>&quot;ITU-R P676-9&quot;</STRING>
                                    </VAR>
                                    <VAR name = "UserComment">
                                        <STRING>&quot;ITU-R P676-9 gaseous absorption model&quot;</STRING>
                                    </VAR>
                                    <VAR name = "ReadOnly">
                                        <BOOL>false</BOOL>
                                    </VAR>
                                    <VAR name = "Clonable">
                                        <BOOL>true</BOOL>
                                    </VAR>
                                    <VAR name = "Category">
                                        <STRING>&quot;@Top&quot;</STRING>
                                    </VAR>
                                    <VAR name = "UseApproxMethod">
                                        <BOOL>true</BOOL>
                                    </VAR>
                                    <VAR name = "UseSeasonalRegional">
                                        <BOOL>true</BOOL>
                                    </VAR>
                                </SCOPE>
                            </VAR>
                        </VAR>
                    </SCOPE>
                </VAR>
            </VAR>
            <VAR name = "UseUrbanTerresPropLossModel">
                <BOOL>false</BOOL>
            </VAR>
            <VAR name = "UrbanTerresPropLossModel">
                <VAR name = "Two_Ray">
                    <SCOPE Class = "LinkEmbedControl">
                        <VAR name = "ReferenceType">
                            <STRING>&quot;Unlinked&quot;</STRING>
                        </VAR>
                        <VAR name = "Component">
                            <VAR name = "Two_Ray">
                                <SCOPE Class = "UrbanTerrestrialPropagationLossModel">
                                    <VAR name = "Version">
                                        <STRING>&quot;1.0.0 a&quot;</STRING>
                                    </VAR>
                                    <VAR name = "IdentifierInformation">
                                        <SCOPE>
                                            <VAR name = "Identifier">
                                                <STRING>&quot;{53D1E386-64D4-4536-858D-C2921A72708D}&quot;</STRING>
                                            </VAR>
                                            <VAR name = "Version">
                                                <STRING>&quot;1&quot;</STRING>
                                            </VAR>
                                            <VAR name = "SdfInformation">
                                                <SCOPE>
                                                    <VAR name = "Version">
                                                        <STRING>&quot;0.0&quot;</STRING>
                                                    </VAR>
                                                    <VAR name = "Url">
                                                        <STRING>&quot;&quot;</STRING>
                                                    </VAR>
                                                </SCOPE>
                                            </VAR>
                                            <VAR name = "SourceIdentifierInformation">
                                                <SCOPE>
                                                    <VAR name = "Identifier">
                                                        <STRING>&quot;{60FA4C9B-5D74-4743-A449-66CEB6DFC97B}&quot;</STRING>
                                                    </VAR>
                                                    <VAR name = "Version">
                                                        <STRING>&quot;1&quot;</STRING>
                                                    </VAR>
                                                    <VAR name = "SdfInformation">
                                                        <SCOPE>
                                                            <VAR name = "Version">
                                                                <STRING>&quot;0.0&quot;</STRING>
                                                            </VAR>
                                                            <VAR name = "Url">
                                                                <STRING>&quot;&quot;</STRING>
                                                            </VAR>
                                                        </SCOPE>
                                                    </VAR>
                                                </SCOPE>
                                            </VAR>
                                        </SCOPE>
                                    </VAR>
                                    <VAR name = "ComponentName">
                                        <STRING>&quot;Two_Ray&quot;</STRING>
                                    </VAR>
                                    <VAR name = "Description">
                                        <STRING>&quot;Two Ray (Fourth Power Law) atmospheric absorption model&quot;</STRING>
                                    </VAR>
                                    <VAR name = "Type">
                                        <STRING>&quot;Two Ray&quot;</STRING>
                                    </VAR>
                                    <VAR name = "UserComment">
                                        <STRING>&quot;Two Ray (Fourth Power Law) atmospheric absorption model&quot;</STRING>
                                    </VAR>
                                    <VAR name = "ReadOnly">
                                        <BOOL>false</BOOL>
                                    </VAR>
                                    <VAR name = "Clonable">
                                        <BOOL>true</BOOL>
                                    </VAR>
                                    <VAR name = "Category">
                                        <STRING>&quot;@Top&quot;</STRING>
                                    </VAR>
                                    <VAR name = "SurfaceTemperature">
                                        <QUANTITY Dimension = "Temperature" Unit = "K">
                                            <REAL>273.15</REAL>
                                        </QUANTITY>
                                    </VAR>
                                    <VAR name = "LossFactor">
                                        <REAL>1</REAL>
                                    </VAR>
                                </SCOPE>
                            </VAR>
                        </VAR>
                    </SCOPE>
                </VAR>
            </VAR>
            <VAR name = "UseCustomA">
                <BOOL>false</BOOL>
            </VAR>
            <VAR name = "UseCustomB">
                <BOOL>false</BOOL>
            </VAR>
            <VAR name = "UseCustomC">
                <BOOL>false</BOOL>
            </VAR>
        </SCOPE>
    </VAR>
    <VAR name = "EarthTemperature">
        <QUANTITY Dimension = "Temperature" Unit = "K">
            <REAL>290</REAL>
        </QUANTITY>
    </VAR>
    <VAR name = "RainOutagePercent">
        <REAL>0.1</REAL>
    </VAR>
    <VAR name = "ActiveCommSystem">
        <LINKTOOBJ>
            <STRING>&quot;None&quot;</STRING>
        </LINKTOOBJ>
    </VAR>
    <VAR name = "MagneticNorthPoleLatitude">
        <QUANTITY Dimension = "AngleUnit" Unit = "rad">
            <REAL>1.387536755335492</REAL>
        </QUANTITY>
    </VAR>
    <VAR name = "MagneticNorthPoleLongitude">
        <QUANTITY Dimension = "AngleUnit" Unit = "rad">
            <REAL>-1.204277183876087</REAL>
        </QUANTITY>
    </VAR>
</SCOPE>        END RfEnv

        BEGIN LaserEnv
<?xml version = "1.0" standalone = "yes"?>
<SCOPE>
    <VAR name = "PropagationChannel">
        <SCOPE>
            <VAR name = "EnableAtmosphericLossModel">
                <BOOL>false</BOOL>
            </VAR>
            <VAR name = "AtmosphericLossModel">
                <VAR name = "Beer-Bouguer-Lambert_Law">
                    <SCOPE Class = "LinkEmbedControl">
                        <VAR name = "ReferenceType">
                            <STRING>&quot;Unlinked&quot;</STRING>
                        </VAR>
                        <VAR name = "Component">
                            <VAR name = "Beer-Bouguer-Lambert_Law">
                                <SCOPE Class = "LaserAtmosphericAbsorptionLossModel">
                                    <VAR name = "Version">
                                        <STRING>&quot;1.0.0 a&quot;</STRING>
                                    </VAR>
                                    <VAR name = "IdentifierInformation">
                                        <SCOPE>
                                            <VAR name = "Identifier">
                                                <STRING>&quot;{EAC78DF9-E01A-4D82-9949-292E01EF5BCB}&quot;</STRING>
                                            </VAR>
                                            <VAR name = "Version">
                                                <STRING>&quot;1&quot;</STRING>
                                            </VAR>
                                            <VAR name = "SdfInformation">
                                                <SCOPE>
                                                    <VAR name = "Version">
                                                        <STRING>&quot;0.0&quot;</STRING>
                                                    </VAR>
                                                    <VAR name = "Url">
                                                        <STRING>&quot;&quot;</STRING>
                                                    </VAR>
                                                </SCOPE>
                                            </VAR>
                                            <VAR name = "SourceIdentifierInformation">
                                                <SCOPE>
                                                    <VAR name = "Identifier">
                                                        <STRING>&quot;{6896684B-630D-472D-8027-385684842E74}&quot;</STRING>
                                                    </VAR>
                                                    <VAR name = "Version">
                                                        <STRING>&quot;1&quot;</STRING>
                                                    </VAR>
                                                    <VAR name = "SdfInformation">
                                                        <SCOPE>
                                                            <VAR name = "Version">
                                                                <STRING>&quot;0.0&quot;</STRING>
                                                            </VAR>
                                                            <VAR name = "Url">
                                                                <STRING>&quot;&quot;</STRING>
                                                            </VAR>
                                                        </SCOPE>
                                                    </VAR>
                                                </SCOPE>
                                            </VAR>
                                        </SCOPE>
                                    </VAR>
                                    <VAR name = "ComponentName">
                                        <STRING>&quot;Beer-Bouguer-Lambert_Law&quot;</STRING>
                                    </VAR>
                                    <VAR name = "Description">
                                        <STRING>&quot;Model atmospheric loss for laser receivers using the Beer-Bouguer-Lambert Law&quot;</STRING>
                                    </VAR>
                                    <VAR name = "Type">
                                        <STRING>&quot;Beer-Bouguer-Lambert Law&quot;</STRING>
                                    </VAR>
                                    <VAR name = "UserComment">
                                        <STRING>&quot;Model atmospheric loss for laser receivers using the Beer-Bouguer-Lambert Law&quot;</STRING>
                                    </VAR>
                                    <VAR name = "ReadOnly">
                                        <BOOL>false</BOOL>
                                    </VAR>
                                    <VAR name = "Clonable">
                                        <BOOL>true</BOOL>
                                    </VAR>
                                    <VAR name = "Category">
                                        <STRING>&quot;@Top&quot;</STRING>
                                    </VAR>
                                    <VAR name = "LayerList">
                                        <LIST>
                                            <SCOPE>
                                                <VAR name = "LayerNum">
                                                    <INT>1</INT>
                                                </VAR>
                                                <VAR name = "LayerTop">
                                                    <QUANTITY Dimension = "DistanceUnit" Unit = "m">
                                                        <REAL>100000</REAL>
                                                    </QUANTITY>
                                                </VAR>
                                                <VAR name = "ExtinctionCoefficient">
                                                    <QUANTITY Dimension = "UnitlessPerSmallDistance" Unit = "m^-1">
                                                        <REAL>0</REAL>
                                                    </QUANTITY>
                                                </VAR>
                                            </SCOPE>
                                        </LIST>
                                    </VAR>
                                    <VAR name = "EnableEvenlySpacedHeights">
                                        <BOOL>true</BOOL>
                                    </VAR>
                                    <VAR name = "MaxLayerHeight">
                                        <QUANTITY Dimension = "DistanceUnit" Unit = "m">
                                            <REAL>100000</REAL>
                                        </QUANTITY>
                                    </VAR>
                                </SCOPE>
                            </VAR>
                        </VAR>
                    </SCOPE>
                </VAR>
            </VAR>
            <VAR name = "EnableTropoScintLossModel">
                <BOOL>false</BOOL>
            </VAR>
            <VAR name = "TropoScintLossModel">
                <VAR name = "ITU-R_P1814">
                    <SCOPE Class = "LinkEmbedControl">
                        <VAR name = "ReferenceType">
                            <STRING>&quot;Unlinked&quot;</STRING>
                        </VAR>
                        <VAR name = "Component">
                            <VAR name = "ITU-R_P1814">
                                <SCOPE Class = "LaserTropoScintLossModel">
                                    <VAR name = "Version">
                                        <STRING>&quot;1.0.0 a&quot;</STRING>
                                    </VAR>
                                    <VAR name = "IdentifierInformation">
                                        <SCOPE>
                                            <VAR name = "Identifier">
                                                <STRING>&quot;{0E0B92E1-99C4-4FDE-8F11-424D07AE40C0}&quot;</STRING>
                                            </VAR>
                                            <VAR name = "Version">
                                                <STRING>&quot;1&quot;</STRING>
                                            </VAR>
                                            <VAR name = "SdfInformation">
                                                <SCOPE>
                                                    <VAR name = "Version">
                                                        <STRING>&quot;0.0&quot;</STRING>
                                                    </VAR>
                                                    <VAR name = "Url">
                                                        <STRING>&quot;&quot;</STRING>
                                                    </VAR>
                                                </SCOPE>
                                            </VAR>
                                            <VAR name = "SourceIdentifierInformation">
                                                <SCOPE>
                                                    <VAR name = "Identifier">
                                                        <STRING>&quot;{651AF2C8-7D6D-457E-8F99-1FB796A460BF}&quot;</STRING>
                                                    </VAR>
                                                    <VAR name = "Version">
                                                        <STRING>&quot;1&quot;</STRING>
                                                    </VAR>
                                                    <VAR name = "SdfInformation">
                                                        <SCOPE>
                                                            <VAR name = "Version">
                                                                <STRING>&quot;0.0&quot;</STRING>
                                                            </VAR>
                                                            <VAR name = "Url">
                                                                <STRING>&quot;&quot;</STRING>
                                                            </VAR>
                                                        </SCOPE>
                                                    </VAR>
                                                </SCOPE>
                                            </VAR>
                                        </SCOPE>
                                    </VAR>
                                    <VAR name = "ComponentName">
                                        <STRING>&quot;ITU-R_P1814&quot;</STRING>
                                    </VAR>
                                    <VAR name = "Description">
                                        <STRING>&quot;ITU-R P1814&quot;</STRING>
                                    </VAR>
                                    <VAR name = "Type">
                                        <STRING>&quot;ITU-R P1814&quot;</STRING>
                                    </VAR>
                                    <VAR name = "UserComment">
                                        <STRING>&quot;ITU-R P1814&quot;</STRING>
                                    </VAR>
                                    <VAR name = "ReadOnly">
                                        <BOOL>false</BOOL>
                                    </VAR>
                                    <VAR name = "Clonable">
                                        <BOOL>true</BOOL>
                                    </VAR>
                                    <VAR name = "Category">
                                        <STRING>&quot;@Top&quot;</STRING>
                                    </VAR>
                                    <VAR name = "AtmosphericTurbulenceModel">
                                        <VAR name = "Constant">
                                            <SCOPE Class = "AtmosphericTurbulenceModel">
                                                <VAR name = "ConstantRefractiveIndexStructureParameter">
                                                    <REAL>1.7e-14</REAL>
                                                </VAR>
                                                <VAR name = "Type">
                                                    <STRING>&quot;Constant&quot;</STRING>
                                                </VAR>
                                            </SCOPE>
                                        </VAR>
                                    </VAR>
                                </SCOPE>
                            </VAR>
                        </VAR>
                    </SCOPE>
                </VAR>
            </VAR>
        </SCOPE>
    </VAR>
</SCOPE>        END LaserEnv

        BEGIN ComponentManager
        END ComponentManager

        BEGIN RadarCrossSection
<?xml version = "1.0" standalone = "yes"?>
<SCOPE>
    <VAR name = "Model">
        <VAR name = "Radar_Cross_Section">
            <SCOPE Class = "LinkEmbedControl">
                <VAR name = "ReferenceType">
                    <STRING>&quot;Unlinked&quot;</STRING>
                </VAR>
                <VAR name = "Component">
                    <VAR name = "Radar_Cross_Section">
                        <SCOPE Class = "RCS">
                            <VAR name = "Version">
                                <STRING>&quot;1.0.0 a&quot;</STRING>
                            </VAR>
                            <VAR name = "IdentifierInformation">
                                <SCOPE>
                                    <VAR name = "Identifier">
                                        <STRING>&quot;{99C18647-F460-4EB2-9889-8CBC9530EFE6}&quot;</STRING>
                                    </VAR>
                                    <VAR name = "Version">
                                        <STRING>&quot;1&quot;</STRING>
                                    </VAR>
                                    <VAR name = "SdfInformation">
                                        <SCOPE>
                                            <VAR name = "Version">
                                                <STRING>&quot;0.0&quot;</STRING>
                                            </VAR>
                                            <VAR name = "Url">
                                                <STRING>&quot;&quot;</STRING>
                                            </VAR>
                                        </SCOPE>
                                    </VAR>
                                    <VAR name = "SourceIdentifierInformation">
                                        <SCOPE>
                                            <VAR name = "Identifier">
                                                <STRING>&quot;{EF03E656-5AB7-4F70-A363-4753683F2BD4}&quot;</STRING>
                                            </VAR>
                                            <VAR name = "Version">
                                                <STRING>&quot;1&quot;</STRING>
                                            </VAR>
                                            <VAR name = "SdfInformation">
                                                <SCOPE>
                                                    <VAR name = "Version">
                                                        <STRING>&quot;0.0&quot;</STRING>
                                                    </VAR>
                                                    <VAR name = "Url">
                                                        <STRING>&quot;&quot;</STRING>
                                                    </VAR>
                                                </SCOPE>
                                            </VAR>
                                        </SCOPE>
                                    </VAR>
                                </SCOPE>
                            </VAR>
                            <VAR name = "ComponentName">
                                <STRING>&quot;Radar_Cross_Section&quot;</STRING>
                            </VAR>
                            <VAR name = "Description">
                                <STRING>&quot;Radar Cross Section&quot;</STRING>
                            </VAR>
                            <VAR name = "Type">
                                <STRING>&quot;Radar Cross Section&quot;</STRING>
                            </VAR>
                            <VAR name = "UserComment">
                                <STRING>&quot;Radar Cross Section&quot;</STRING>
                            </VAR>
                            <VAR name = "ReadOnly">
                                <BOOL>false</BOOL>
                            </VAR>
                            <VAR name = "Clonable">
                                <BOOL>true</BOOL>
                            </VAR>
                            <VAR name = "Category">
                                <STRING>&quot;@Top&quot;</STRING>
                            </VAR>
                            <VAR name = "FrequencyBandList">
                                <LIST>
                                    <SCOPE>
                                        <VAR name = "MinFrequency">
                                            <QUANTITY Dimension = "BandwidthUnit" Unit = "Hz">
                                                <REAL>2997920</REAL>
                                            </QUANTITY>
                                        </VAR>
                                        <VAR name = "ComputeTypeStrategy">
                                            <VAR name = "Constant Value">
                                                <SCOPE Class = "RCS Compute Strategy">
                                                    <VAR name = "ConstantValue">
                                                        <QUANTITY Dimension = "RcsUnit" Unit = "sqm">
                                                            <REAL>1</REAL>
                                                        </QUANTITY>
                                                    </VAR>
                                                    <VAR name = "Type">
                                                        <STRING>&quot;Constant Value&quot;</STRING>
                                                    </VAR>
                                                    <VAR name = "ComponentName">
                                                        <STRING>&quot;Constant Value&quot;</STRING>
                                                    </VAR>
                                                </SCOPE>
                                            </VAR>
                                        </VAR>
                                        <VAR name = "SwerlingCase">
                                            <STRING>&quot;0&quot;</STRING>
                                        </VAR>
                                    </SCOPE>
                                </LIST>
                            </VAR>
                        </SCOPE>
                    </VAR>
                </VAR>
            </SCOPE>
        </VAR>
    </VAR>
</SCOPE>        END RadarCrossSection

        BEGIN Gator
            RPOComponentsLoaded		 False
        END Gator

        BEGIN Crdn
        END Crdn

        BEGIN SpiceExt
            OutputErrorMsgsOnLoad		 No
            SpiceFile		 "planets.bsp"
        END SpiceExt

        BEGIN FlightScenExt
        END FlightScenExt

        BEGIN Graphics

            BEGIN Animation

                StartTime		 12 Nov 2026 02:00:00.000000000
                EndTime		 12 Nov 2026 02:10:00.000000000
                CurrentTime		 12 Nov 2026 02:00:00.000000000
                Direction		 Forward
                UpdateDelta		 10
                RefreshDelta		 0.010000
                XRealTimeMult		 1
                RealTimeOffset		 0
                XRtStartFromPause		                Yes		
                TimeArrayIncrement		 1

            END Animation


            BEGIN DisplayFlags
                ShowLabels		 On
                ShowPassLabel		 Off
                ShowElsetNum		 Off
                ShowGndTracks		 On
                ShowGndMarkers		 On
                ShowOrbitMarkers		 On
                ShowPlanetOrbits		 Off
                ShowPlanetCBIPos		 On
                ShowPlanetCBILabel		 On
                ShowPlanetGndPos		 On
                ShowPlanetGndLabel		 On
                ShowSensors		 On
                ShowWayptMarkers		 Off
                ShowWayptTurnMarkers		 Off
                ShowOrbits		 On
                ShowDtedRegions		 Off
                ShowAreaTgtCentroids		 On
                ShowToolBar		 On
                ShowStatusBar		 On
                ShowScrollBars		 On
                AllowAnimUpdate		 On
                AccShowLine		 On
                AccAnimHigh		 On
                AccStatHigh		 On
                AccAnimLineLineWidth		  1.0000000000000000e+00
                ShowPrintButton		 On
                ShowAnimButtons		 On
                ShowAnimModeButtons		 On
                ShowZoomMsrButtons		 On
                ShowMapCbButton		 Off
            END DisplayFlags

            BEGIN WinFonts

                Consolas,12,700,0
                Consolas,14,700,0
                Consolas,16,700,0

            END WinFonts

            BEGIN MapData

                BEGIN TerrainConverterData
                    NorthLat		  0.0000000000000000e+00
                    EastLon		  0.0000000000000000e+00
                    SouthLat		  0.0000000000000000e+00
                    WestLon		  0.0000000000000000e+00
                    ColorByRGB		 No
                    AltsFromMSL		 No
                    UseColorRamp		 Yes
                    UseRegionMinMax		 Yes
                    SizeSameAsSrc		 Yes
                    MinAltHSV		  0.0000000000000000e+00  6.9999999999999996e-01  8.0000000000000004e-01  4.0000000000000002e-01
                    MaxAltHSV		  1.0000000000000000e+06  0.0000000000000000e+00  2.0000000000000001e-01  1.0000000000000000e+00
                    SmoothColors		 Yes
                    CreateChunkTrn		 No
                    OutputFormat		 PDTTX
                END TerrainConverterData

                DisableDefKbdActions		 Off
                TextShadowStyle		 Dark
                TextShadowColor		 #000000
                BingLevelOfDetailScale		 2
                BEGIN Map
                    MapNum		 1
                    TrackingMode		 LatLon
                    PickEnabled		 On
                    PanEnabled		 On

                    BEGIN MapAttributes
                        PrimaryBody		 Earth
                        SecondaryBody		 Sun
                        CenterLatitude		 0
                        CenterLongitude		 0
                        ProjectionAltitude		 63621860
                        FieldOfView		 35
                        OrthoDisplayDistance		 20000000
                        TransformTrajectory		 On
                        EquatorialRadius		 6378137
                        BackgroundColor		 #000000
                        LatLonLines		 On
                        LatSpacing		 30
                        LonSpacing		 30
                        LatLonLineColor		 #999999
                        LatLonLineStyle		 2
                        ShowOrthoDistGrid		 Off
                        OrthoGridXSpacing		 5
                        OrthoGridYSpacing		 5
                        OrthoGridColor		 #ffffff
                        ShowImageExtents		 Off
                        ImageExtentLineColor		 #ffffff
                        ImageExtentLineStyle		 0
                        ImageExtentLineWidth		 1
                        ShowImageNames		 Off
                        ImageNameFont		 0
                        Projection		 EquidistantCylindrical
                        Resolution		 VeryLow
                        CoordinateSys		 ECF
                        UseBackgroundImage		 On
                        UseBingForBackground		 On
                        BingType		 Aerial
                        BingLogoHorizAlign		 Right
                        BingLogoVertAlign		 Bottom
                        BackgroundImageFile		 Basic.bmp
                        UseNightLights		 Off
                        NightLightsFactor		 3.5
                        UseCloudsFile		 Off
                        BEGIN ZoomLocations
                            BEGIN ZoomLocation
                                CenterLat		 0
                                CenterLon		 0
                                ZoomWidth		 360
                                ZoomHeight		 180
                            END ZoomLocation
                        END ZoomLocations
                        UseVarAspectRatio		 No
                        SwapMapResolution		 Yes
                        NoneToVLowSwapDist		 2000000
                        VLowToLowSwapDist		 20000
                        LowToMediumSwapDist		 10000
                        MediumToHighSwapDist		 5000
                        HighToVHighSwapDist		 1000
                        VHighToSHighSwapDist		 100
                        BEGIN Axes
                            DisplayAxes		 no
                            CoordSys		 CBI
                            2aryCB		 Sun
                            Display+x		 yes
                            Label+x		 yes
                            Color+x		 #ffffff
                            Scale+x		 3
                            Display-x		 yes
                            Label-x		 yes
                            Color-x		 #ffffff
                            Scale-x		 3
                            Display+y		 yes
                            Label+y		 yes
                            Color+y		 #ffffff
                            Scale+y		 3
                            Display-y		 yes
                            Label-y		 yes
                            Color-y		 #ffffff
                            Scale-y		 3
                            Display+z		 yes
                            Label+z		 yes
                            Color+z		 #ffffff
                            Scale+z		 3
                            Display-z		 yes
                            Label-z		 yes
                            Color-z		 #ffffff
                            Scale-z		 3
                        END Axes

                    END MapAttributes

                    BEGIN MapList
                        BEGIN Detail
                            Alias		 RWDB2_Coastlines
                            Show		 Yes
                            Color		 #8fbc8f
                        END Detail
                        BEGIN Detail
                            Alias		 RWDB2_International_Borders
                            Show		 No
                            Color		 #8fbc8f
                        END Detail
                        BEGIN Detail
                            Alias		 RWDB2_Islands
                            Show		 No
                            Color		 #8fbc8f
                        END Detail
                        BEGIN Detail
                            Alias		 RWDB2_Lakes
                            Show		 No
                            Color		 #87cefa
                        END Detail
                        BEGIN Detail
                            Alias		 RWDB2_Provincial_Borders
                            Show		 No
                            Color		 #8fbc8f
                        END Detail
                        BEGIN Detail
                            Alias		 RWDB2_Rivers
                            Show		 No
                            Color		 #87cefa
                        END Detail
                    END MapList


                    BEGIN MapAnnotations
                    END MapAnnotations

                    BEGIN DisplayFlags
                        ShowLabels		 On
                        ShowPassLabel		 Off
                        ShowElsetNum		 Off
                        ShowGndTracks		 On
                        ShowGndMarkers		 On
                        ShowOrbitMarkers		 On
                        ShowPlanetOrbits		 Off
                        ShowPlanetCBIPos		 On
                        ShowPlanetCBILabel		 On
                        ShowPlanetGndPos		 On
                        ShowPlanetGndLabel		 On
                        ShowSensors		 On
                        ShowWayptMarkers		 Off
                        ShowWayptTurnMarkers		 Off
                        ShowOrbits		 On
                        ShowDtedRegions		 Off
                        ShowAreaTgtCentroids		 On
                        ShowToolBar		 On
                        ShowStatusBar		 On
                        ShowScrollBars		 On
                        AllowAnimUpdate		 Off
                        AccShowLine		 On
                        AccAnimHigh		 On
                        AccStatHigh		 On
                        AccAnimLineLineWidth		  1.0000000000000000e+00
                        ShowPrintButton		 On
                        ShowAnimButtons		 On
                        ShowAnimModeButtons		 On
                        ShowZoomMsrButtons		 On
                        ShowMapCbButton		 Off
                    END DisplayFlags

                    BEGIN RecordMovie
                        OutputFormat		 VIDEO
                        SdfSelected		 No
                        Directory		 C:\Users\20828\Documents\STK 12
                        BaseName		 Frame
                        Digits		 4
                        Frame		 0
                        LastAnimTime		 0
                        OutputMode		 Normal
                        HiResAssembly		 Assemble
                        HRWidth		 6000
                        HRHeight		 4500
                        HRDPI		 600
                        UseSnapInterval		 No
                        SnapInterval		 0
                        VideoCodec		 "H264"
                        Framerate		 30
                        Bitrate		 10000000
                    END RecordMovie


                    BEGIN TimeDisplay
                        Show		 0
                        TextColor		 #ffffff
                        TextTranslucency		 0
                        ShowBackground		 0
                        BackColor		 #4d4d4d
                        BackTranslucency		 0.4
                        XPosition		 20
                        YPosition		 -20
                    END TimeDisplay

                    BEGIN LightingData
                        DisplayAltitude		 0
                        SubsolarPoint		 Off
                        SubsolarPointColor		 #ffff00
                        SubsolarPointMarkerStyle		 2

                        ShowUmbraLine		 Off
                        UmbraLineColor		 #000000
                        UmbraLineStyle		 0
                        UmbraLineWidth		 2
                        FillUmbra		 On
                        UmbraFillColor		 #000000
                        ShowSunlightLine		 Off
                        SunlightLineColor		 #ffff00
                        SunlightLineStyle		 0
                        SunlightLineWidth		 2
                        FillSunlight		 On
                        SunlightFillColor		 #ffffff
                        SunlightMinOpacity		 0
                        SunlightMaxOpacity		 0.2
                        UmbraMaxOpacity		 0.7
                        UmbraMinOpacity		 0.4
                    END LightingData
                END Map

                BEGIN MapStyles

                    UseStyleTime		 No

                    BEGIN Style
                        Name		 DefaultWithBing
                        Time		 1130400
                        UpdateDelta		 10

                        BEGIN MapAttributes
                            PrimaryBody		 Earth
                            SecondaryBody		 Sun
                            CenterLatitude		 0
                            CenterLongitude		 0
                            ProjectionAltitude		 63621860
                            FieldOfView		 35
                            OrthoDisplayDistance		 20000000
                            TransformTrajectory		 On
                            EquatorialRadius		 6378137
                            BackgroundColor		 #000000
                            LatLonLines		 On
                            LatSpacing		 30
                            LonSpacing		 30
                            LatLonLineColor		 #999999
                            LatLonLineStyle		 2
                            ShowOrthoDistGrid		 Off
                            OrthoGridXSpacing		 5
                            OrthoGridYSpacing		 5
                            OrthoGridColor		 #ffffff
                            ShowImageExtents		 Off
                            ImageExtentLineColor		 #ffffff
                            ImageExtentLineStyle		 0
                            ImageExtentLineWidth		 1
                            ShowImageNames		 Off
                            ImageNameFont		 0
                            Projection		 EquidistantCylindrical
                            Resolution		 VeryLow
                            CoordinateSys		 ECF
                            UseBackgroundImage		 On
                            UseBingForBackground		 On
                            BingType		 Aerial
                            BingLogoHorizAlign		 Right
                            BingLogoVertAlign		 Bottom
                            BackgroundImageFile		 Basic.bmp
                            UseNightLights		 Off
                            NightLightsFactor		 3.5
                            UseCloudsFile		 Off
                            BEGIN ZoomLocations
                                BEGIN ZoomLocation
                                    CenterLat		 0
                                    CenterLon		 0
                                    ZoomWidth		 359.999998
                                    ZoomHeight		 180
                                END ZoomLocation
                            END ZoomLocations
                            UseVarAspectRatio		 No
                            SwapMapResolution		 Yes
                            NoneToVLowSwapDist		 2000000
                            VLowToLowSwapDist		 20000
                            LowToMediumSwapDist		 10000
                            MediumToHighSwapDist		 5000
                            HighToVHighSwapDist		 1000
                            VHighToSHighSwapDist		 100
                            BEGIN Axes
                                DisplayAxes		 no
                                CoordSys		 CBI
                                2aryCB		 Sun
                                Display+x		 yes
                                Label+x		 yes
                                Color+x		 #ffffff
                                Scale+x		 3
                                Display-x		 yes
                                Label-x		 yes
                                Color-x		 #ffffff
                                Scale-x		 3
                                Display+y		 yes
                                Label+y		 yes
                                Color+y		 #ffffff
                                Scale+y		 3
                                Display-y		 yes
                                Label-y		 yes
                                Color-y		 #ffffff
                                Scale-y		 3
                                Display+z		 yes
                                Label+z		 yes
                                Color+z		 #ffffff
                                Scale+z		 3
                                Display-z		 yes
                                Label-z		 yes
                                Color-z		 #ffffff
                                Scale-z		 3
                            END Axes

                        END MapAttributes

                        BEGIN MapList
                            BEGIN Detail
                                Alias		 RWDB2_Coastlines
                                Show		 Yes
                                Color		 #8fbc8f
                            END Detail
                            BEGIN Detail
                                Alias		 RWDB2_International_Borders
                                Show		 No
                                Color		 #8fbc8f
                            END Detail
                            BEGIN Detail
                                Alias		 RWDB2_Islands
                                Show		 No
                                Color		 #8fbc8f
                            END Detail
                            BEGIN Detail
                                Alias		 RWDB2_Lakes
                                Show		 No
                                Color		 #87cefa
                            END Detail
                            BEGIN Detail
                                Alias		 RWDB2_Provincial_Borders
                                Show		 No
                                Color		 #8fbc8f
                            END Detail
                            BEGIN Detail
                                Alias		 RWDB2_Rivers
                                Show		 No
                                Color		 #87cefa
                            END Detail
                        END MapList


                        BEGIN MapAnnotations
                        END MapAnnotations

                        BEGIN RecordMovie
                            OutputFormat		 VIDEO
                            SdfSelected		 No
                            Directory		 C:\Users\20828\Documents\STK 12
                            BaseName		 Frame
                            Digits		 4
                            Frame		 0
                            LastAnimTime		 0
                            OutputMode		 Normal
                            HiResAssembly		 Assemble
                            HRWidth		 6000
                            HRHeight		 4500
                            HRDPI		 600
                            UseSnapInterval		 No
                            SnapInterval		 0
                            VideoCodec		 "H264"
                            Framerate		 30
                            Bitrate		 10000000
                        END RecordMovie


                        BEGIN TimeDisplay
                            Show		 0
                            TextColor		 #ffffff
                            TextTranslucency		 0
                            ShowBackground		 0
                            BackColor		 #4d4d4d
                            BackTranslucency		 0.4
                            XPosition		 20
                            YPosition		 -20
                        END TimeDisplay

                        BEGIN LightingData
                            DisplayAltitude		 0
                            SubsolarPoint		 Off
                            SubsolarPointColor		 #ffff00
                            SubsolarPointMarkerStyle		 2

                            ShowUmbraLine		 Off
                            UmbraLineColor		 #000000
                            UmbraLineStyle		 0
                            UmbraLineWidth		 2
                            FillUmbra		 On
                            UmbraFillColor		 #000000
                            ShowSunlightLine		 Off
                            SunlightLineColor		 #ffff00
                            SunlightLineStyle		 0
                            SunlightLineWidth		 2
                            FillSunlight		 On
                            SunlightFillColor		 #ffffff
                            SunlightMinOpacity		 0
                            SunlightMaxOpacity		 0.2
                            UmbraMaxOpacity		 0.7
                            UmbraMinOpacity		 0.4
                        END LightingData

                        ShowDtedRegions		 Off

                    END Style

                    BEGIN Style
                        Name		 DefaultWithoutBing
                        Time		 1130400
                        UpdateDelta		 10

                        BEGIN MapAttributes
                            PrimaryBody		 Earth
                            SecondaryBody		 Sun
                            CenterLatitude		 0
                            CenterLongitude		 0
                            ProjectionAltitude		 63621860
                            FieldOfView		 35
                            OrthoDisplayDistance		 20000000
                            TransformTrajectory		 On
                            EquatorialRadius		 6378137
                            BackgroundColor		 #000000
                            LatLonLines		 On
                            LatSpacing		 30
                            LonSpacing		 30
                            LatLonLineColor		 #999999
                            LatLonLineStyle		 2
                            ShowOrthoDistGrid		 Off
                            OrthoGridXSpacing		 5
                            OrthoGridYSpacing		 5
                            OrthoGridColor		 #ffffff
                            ShowImageExtents		 Off
                            ImageExtentLineColor		 #ffffff
                            ImageExtentLineStyle		 0
                            ImageExtentLineWidth		 1
                            ShowImageNames		 Off
                            ImageNameFont		 0
                            Projection		 EquidistantCylindrical
                            Resolution		 VeryLow
                            CoordinateSys		 ECF
                            UseBackgroundImage		 On
                            UseBingForBackground		 Off
                            BingType		 Aerial
                            BingLogoHorizAlign		 Right
                            BingLogoVertAlign		 Bottom
                            BackgroundImageFile		 Basic.bmp
                            UseNightLights		 Off
                            NightLightsFactor		 3.5
                            UseCloudsFile		 Off
                            BEGIN ZoomLocations
                                BEGIN ZoomLocation
                                    CenterLat		 0
                                    CenterLon		 0
                                    ZoomWidth		 359.999998
                                    ZoomHeight		 180
                                END ZoomLocation
                            END ZoomLocations
                            UseVarAspectRatio		 No
                            SwapMapResolution		 Yes
                            NoneToVLowSwapDist		 2000000
                            VLowToLowSwapDist		 20000
                            LowToMediumSwapDist		 10000
                            MediumToHighSwapDist		 5000
                            HighToVHighSwapDist		 1000
                            VHighToSHighSwapDist		 100
                            BEGIN Axes
                                DisplayAxes		 no
                                CoordSys		 CBI
                                2aryCB		 Sun
                                Display+x		 yes
                                Label+x		 yes
                                Color+x		 #ffffff
                                Scale+x		 3
                                Display-x		 yes
                                Label-x		 yes
                                Color-x		 #ffffff
                                Scale-x		 3
                                Display+y		 yes
                                Label+y		 yes
                                Color+y		 #ffffff
                                Scale+y		 3
                                Display-y		 yes
                                Label-y		 yes
                                Color-y		 #ffffff
                                Scale-y		 3
                                Display+z		 yes
                                Label+z		 yes
                                Color+z		 #ffffff
                                Scale+z		 3
                                Display-z		 yes
                                Label-z		 yes
                                Color-z		 #ffffff
                                Scale-z		 3
                            END Axes

                        END MapAttributes

                        BEGIN MapList
                            BEGIN Detail
                                Alias		 RWDB2_Coastlines
                                Show		 Yes
                                Color		 #8fbc8f
                            END Detail
                            BEGIN Detail
                                Alias		 RWDB2_International_Borders
                                Show		 No
                                Color		 #8fbc8f
                            END Detail
                            BEGIN Detail
                                Alias		 RWDB2_Islands
                                Show		 No
                                Color		 #8fbc8f
                            END Detail
                            BEGIN Detail
                                Alias		 RWDB2_Lakes
                                Show		 No
                                Color		 #87cefa
                            END Detail
                            BEGIN Detail
                                Alias		 RWDB2_Provincial_Borders
                                Show		 No
                                Color		 #8fbc8f
                            END Detail
                            BEGIN Detail
                                Alias		 RWDB2_Rivers
                                Show		 No
                                Color		 #87cefa
                            END Detail
                        END MapList


                        BEGIN MapAnnotations
                        END MapAnnotations

                        BEGIN RecordMovie
                            OutputFormat		 VIDEO
                            SdfSelected		 No
                            Directory		 C:\Users\20828\Documents\STK 12
                            BaseName		 Frame
                            Digits		 4
                            Frame		 0
                            LastAnimTime		 0
                            OutputMode		 Normal
                            HiResAssembly		 Assemble
                            HRWidth		 6000
                            HRHeight		 4500
                            HRDPI		 600
                            UseSnapInterval		 No
                            SnapInterval		 0
                            VideoCodec		 "H264"
                            Framerate		 30
                            Bitrate		 3000000
                        END RecordMovie


                        BEGIN TimeDisplay
                            Show		 0
                            TextColor		 #ffffff
                            TextTranslucency		 0
                            ShowBackground		 0
                            BackColor		 #4d4d4d
                            BackTranslucency		 0.4
                            XPosition		 20
                            YPosition		 -20
                        END TimeDisplay

                        BEGIN LightingData
                            DisplayAltitude		 0
                            SubsolarPoint		 Off
                            SubsolarPointColor		 #ffff00
                            SubsolarPointMarkerStyle		 2

                            ShowUmbraLine		 Off
                            UmbraLineColor		 #000000
                            UmbraLineStyle		 0
                            UmbraLineWidth		 2
                            FillUmbra		 On
                            UmbraFillColor		 #000000
                            ShowSunlightLine		 Off
                            SunlightLineColor		 #ffff00
                            SunlightLineStyle		 0
                            SunlightLineWidth		 2
                            FillSunlight		 On
                            SunlightFillColor		 #ffffff
                            SunlightMinOpacity		 0
                            SunlightMaxOpacity		 0.2
                            UmbraMaxOpacity		 0.7
                            UmbraMinOpacity		 0.4
                        END LightingData

                        ShowDtedRegions		 Off

                    END Style

                END MapStyles

            END MapData

            BEGIN GfxClassPref

            END GfxClassPref


            BEGIN ConnectGraphicsOptions

                AsyncPickReturnUnique		 OFF

            END ConnectGraphicsOptions

        END Graphics

        BEGIN Overlays
        END Overlays

        BEGIN VO
        END VO

    END Extensions

    BEGIN SubObjects

        Class Aircraft

            AC1		

        END Class

        Class Facility

            GW1		

        END Class

        Class Satellite

            SAT41917		
            SAT41918		
            SAT41919		
            SAT41920		
            SAT41921		
            SAT41922		
            SAT41923		
            SAT41924		
            SAT41925		
            SAT41926		
            SAT42803		
            SAT42804		
            SAT42805		
            SAT42806		
            SAT42807		
            SAT42808		
            SAT42809		
            SAT42810		
            SAT42811		
            SAT42812		
            SAT42955		
            SAT42956		
            SAT42957		
            SAT42958		
            SAT42959		
            SAT42960		
            SAT42961		
            SAT42962		
            SAT42963		
            SAT42964		
            SAT43070		
            SAT43071		
            SAT43072		
            SAT43073		
            SAT43074		
            SAT43075		
            SAT43076		
            SAT43077		
            SAT43078		
            SAT43079		
            SAT43249		
            SAT43250		
            SAT43251		
            SAT43252		
            SAT43253		
            SAT43254		
            SAT43255		
            SAT43256		
            SAT43257		
            SAT43258		
            SAT43478		
            SAT43479		
            SAT43480		
            SAT43481		
            SAT43482		
            SAT43569		
            SAT43570		
            SAT43571		
            SAT43572		
            SAT43573		
            SAT43574		
            SAT43575		
            SAT43576		
            SAT43577		
            SAT43578		
            SAT43922		
            SAT43923		
            SAT43924		
            SAT43925		
            SAT43926		
            SAT43927		
            SAT43928		
            SAT43929		
            SAT43930		
            SAT43931		
            SAT56726		
            SAT56727		
            SAT56728		
            SAT56729		
            SAT56730		

        END Class

    END SubObjects

    BEGIN References
        Instance *
            *		
        END Instance
        Instance Aircraft/AC1
            Aircraft/AC1		
            Aircraft/AC1/Receiver/D1_ARX1		
            Aircraft/AC1/Sensor/RoofAntennaMask		
            Aircraft/AC1/Transmitter/U1_ATX1		
        END Instance
        Instance Aircraft/AC1/Receiver/D1_ARX1
            Aircraft/AC1/Receiver/D1_ARX1		
        END Instance
        Instance Aircraft/AC1/Sensor/RoofAntennaMask
            *		
            Aircraft/AC1/Sensor/RoofAntennaMask		
        END Instance
        Instance Aircraft/AC1/Transmitter/U1_ATX1
            Aircraft/AC1/Transmitter/U1_ATX1		
        END Instance
        Instance Facility/GW1
            Facility/GW1		
            Facility/GW1/Receiver/FD1_GRX1		
            Facility/GW1/Transmitter/FU1_GTX1		
        END Instance
        Instance Facility/GW1/Receiver/FD1_GRX1
            Facility/GW1/Receiver/FD1_GRX1		
        END Instance
        Instance Facility/GW1/Transmitter/FU1_GTX1
            Facility/GW1/Transmitter/FU1_GTX1		
        END Instance
        Instance Satellite/SAT41917
            Satellite/SAT41917		
            Satellite/SAT41917/Receiver/FU1_SFRX1		
            Satellite/SAT41917/Receiver/U1_SRX1		
            Satellite/SAT41917/Transmitter/D1_STX1		
            Satellite/SAT41917/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT41917/Receiver/FU1_SFRX1
            Satellite/SAT41917/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT41917/Receiver/U1_SRX1
            Satellite/SAT41917/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT41917/Transmitter/D1_STX1
            Satellite/SAT41917/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT41917/Transmitter/FD1_SFTX1
            Satellite/SAT41917/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT41918
            Satellite/SAT41918		
            Satellite/SAT41918/Receiver/FU1_SFRX1		
            Satellite/SAT41918/Receiver/U1_SRX1		
            Satellite/SAT41918/Transmitter/D1_STX1		
            Satellite/SAT41918/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT41918/Receiver/FU1_SFRX1
            Satellite/SAT41918/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT41918/Receiver/U1_SRX1
            Satellite/SAT41918/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT41918/Transmitter/D1_STX1
            Satellite/SAT41918/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT41918/Transmitter/FD1_SFTX1
            Satellite/SAT41918/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT41919
            Satellite/SAT41919		
            Satellite/SAT41919/Receiver/FU1_SFRX1		
            Satellite/SAT41919/Receiver/U1_SRX1		
            Satellite/SAT41919/Transmitter/D1_STX1		
            Satellite/SAT41919/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT41919/Receiver/FU1_SFRX1
            Satellite/SAT41919/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT41919/Receiver/U1_SRX1
            Satellite/SAT41919/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT41919/Transmitter/D1_STX1
            Satellite/SAT41919/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT41919/Transmitter/FD1_SFTX1
            Satellite/SAT41919/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT41920
            Satellite/SAT41920		
            Satellite/SAT41920/Receiver/FU1_SFRX1		
            Satellite/SAT41920/Receiver/U1_SRX1		
            Satellite/SAT41920/Transmitter/D1_STX1		
            Satellite/SAT41920/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT41920/Receiver/FU1_SFRX1
            Satellite/SAT41920/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT41920/Receiver/U1_SRX1
            Satellite/SAT41920/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT41920/Transmitter/D1_STX1
            Satellite/SAT41920/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT41920/Transmitter/FD1_SFTX1
            Satellite/SAT41920/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT41921
            Satellite/SAT41921		
            Satellite/SAT41921/Receiver/FU1_SFRX1		
            Satellite/SAT41921/Receiver/U1_SRX1		
            Satellite/SAT41921/Transmitter/D1_STX1		
            Satellite/SAT41921/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT41921/Receiver/FU1_SFRX1
            Satellite/SAT41921/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT41921/Receiver/U1_SRX1
            Satellite/SAT41921/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT41921/Transmitter/D1_STX1
            Satellite/SAT41921/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT41921/Transmitter/FD1_SFTX1
            Satellite/SAT41921/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT41922
            Satellite/SAT41922		
            Satellite/SAT41922/Receiver/FU1_SFRX1		
            Satellite/SAT41922/Receiver/U1_SRX1		
            Satellite/SAT41922/Transmitter/D1_STX1		
            Satellite/SAT41922/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT41922/Receiver/FU1_SFRX1
            Satellite/SAT41922/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT41922/Receiver/U1_SRX1
            Satellite/SAT41922/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT41922/Transmitter/D1_STX1
            Satellite/SAT41922/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT41922/Transmitter/FD1_SFTX1
            Satellite/SAT41922/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT41923
            Satellite/SAT41923		
            Satellite/SAT41923/Receiver/FU1_SFRX1		
            Satellite/SAT41923/Receiver/U1_SRX1		
            Satellite/SAT41923/Transmitter/D1_STX1		
            Satellite/SAT41923/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT41923/Receiver/FU1_SFRX1
            Satellite/SAT41923/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT41923/Receiver/U1_SRX1
            Satellite/SAT41923/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT41923/Transmitter/D1_STX1
            Satellite/SAT41923/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT41923/Transmitter/FD1_SFTX1
            Satellite/SAT41923/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT41924
            Satellite/SAT41924		
            Satellite/SAT41924/Receiver/FU1_SFRX1		
            Satellite/SAT41924/Receiver/U1_SRX1		
            Satellite/SAT41924/Transmitter/D1_STX1		
            Satellite/SAT41924/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT41924/Receiver/FU1_SFRX1
            Satellite/SAT41924/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT41924/Receiver/U1_SRX1
            Satellite/SAT41924/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT41924/Transmitter/D1_STX1
            Satellite/SAT41924/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT41924/Transmitter/FD1_SFTX1
            Satellite/SAT41924/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT41925
            Satellite/SAT41925		
            Satellite/SAT41925/Receiver/FU1_SFRX1		
            Satellite/SAT41925/Receiver/U1_SRX1		
            Satellite/SAT41925/Transmitter/D1_STX1		
            Satellite/SAT41925/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT41925/Receiver/FU1_SFRX1
            Satellite/SAT41925/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT41925/Receiver/U1_SRX1
            Satellite/SAT41925/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT41925/Transmitter/D1_STX1
            Satellite/SAT41925/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT41925/Transmitter/FD1_SFTX1
            Satellite/SAT41925/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT41926
            Satellite/SAT41926		
            Satellite/SAT41926/Receiver/FU1_SFRX1		
            Satellite/SAT41926/Receiver/U1_SRX1		
            Satellite/SAT41926/Transmitter/D1_STX1		
            Satellite/SAT41926/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT41926/Receiver/FU1_SFRX1
            Satellite/SAT41926/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT41926/Receiver/U1_SRX1
            Satellite/SAT41926/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT41926/Transmitter/D1_STX1
            Satellite/SAT41926/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT41926/Transmitter/FD1_SFTX1
            Satellite/SAT41926/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT42803
            Satellite/SAT42803		
            Satellite/SAT42803/Receiver/FU1_SFRX1		
            Satellite/SAT42803/Receiver/U1_SRX1		
            Satellite/SAT42803/Transmitter/D1_STX1		
            Satellite/SAT42803/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT42803/Receiver/FU1_SFRX1
            Satellite/SAT42803/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT42803/Receiver/U1_SRX1
            Satellite/SAT42803/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT42803/Transmitter/D1_STX1
            Satellite/SAT42803/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT42803/Transmitter/FD1_SFTX1
            Satellite/SAT42803/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT42804
            Satellite/SAT42804		
            Satellite/SAT42804/Receiver/FU1_SFRX1		
            Satellite/SAT42804/Receiver/U1_SRX1		
            Satellite/SAT42804/Transmitter/D1_STX1		
            Satellite/SAT42804/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT42804/Receiver/FU1_SFRX1
            Satellite/SAT42804/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT42804/Receiver/U1_SRX1
            Satellite/SAT42804/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT42804/Transmitter/D1_STX1
            Satellite/SAT42804/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT42804/Transmitter/FD1_SFTX1
            Satellite/SAT42804/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT42805
            Satellite/SAT42805		
            Satellite/SAT42805/Receiver/FU1_SFRX1		
            Satellite/SAT42805/Receiver/U1_SRX1		
            Satellite/SAT42805/Transmitter/D1_STX1		
            Satellite/SAT42805/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT42805/Receiver/FU1_SFRX1
            Satellite/SAT42805/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT42805/Receiver/U1_SRX1
            Satellite/SAT42805/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT42805/Transmitter/D1_STX1
            Satellite/SAT42805/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT42805/Transmitter/FD1_SFTX1
            Satellite/SAT42805/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT42806
            Satellite/SAT42806		
            Satellite/SAT42806/Receiver/FU1_SFRX1		
            Satellite/SAT42806/Receiver/U1_SRX1		
            Satellite/SAT42806/Transmitter/D1_STX1		
            Satellite/SAT42806/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT42806/Receiver/FU1_SFRX1
            Satellite/SAT42806/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT42806/Receiver/U1_SRX1
            Satellite/SAT42806/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT42806/Transmitter/D1_STX1
            Satellite/SAT42806/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT42806/Transmitter/FD1_SFTX1
            Satellite/SAT42806/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT42807
            Satellite/SAT42807		
            Satellite/SAT42807/Receiver/FU1_SFRX1		
            Satellite/SAT42807/Receiver/U1_SRX1		
            Satellite/SAT42807/Transmitter/D1_STX1		
            Satellite/SAT42807/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT42807/Receiver/FU1_SFRX1
            Satellite/SAT42807/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT42807/Receiver/U1_SRX1
            Satellite/SAT42807/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT42807/Transmitter/D1_STX1
            Satellite/SAT42807/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT42807/Transmitter/FD1_SFTX1
            Satellite/SAT42807/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT42808
            Satellite/SAT42808		
            Satellite/SAT42808/Receiver/FU1_SFRX1		
            Satellite/SAT42808/Receiver/U1_SRX1		
            Satellite/SAT42808/Transmitter/D1_STX1		
            Satellite/SAT42808/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT42808/Receiver/FU1_SFRX1
            Satellite/SAT42808/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT42808/Receiver/U1_SRX1
            Satellite/SAT42808/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT42808/Transmitter/D1_STX1
            Satellite/SAT42808/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT42808/Transmitter/FD1_SFTX1
            Satellite/SAT42808/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT42809
            Satellite/SAT42809		
            Satellite/SAT42809/Receiver/FU1_SFRX1		
            Satellite/SAT42809/Receiver/U1_SRX1		
            Satellite/SAT42809/Transmitter/D1_STX1		
            Satellite/SAT42809/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT42809/Receiver/FU1_SFRX1
            Satellite/SAT42809/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT42809/Receiver/U1_SRX1
            Satellite/SAT42809/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT42809/Transmitter/D1_STX1
            Satellite/SAT42809/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT42809/Transmitter/FD1_SFTX1
            Satellite/SAT42809/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT42810
            Satellite/SAT42810		
            Satellite/SAT42810/Receiver/FU1_SFRX1		
            Satellite/SAT42810/Receiver/U1_SRX1		
            Satellite/SAT42810/Transmitter/D1_STX1		
            Satellite/SAT42810/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT42810/Receiver/FU1_SFRX1
            Satellite/SAT42810/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT42810/Receiver/U1_SRX1
            Satellite/SAT42810/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT42810/Transmitter/D1_STX1
            Satellite/SAT42810/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT42810/Transmitter/FD1_SFTX1
            Satellite/SAT42810/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT42811
            Satellite/SAT42811		
            Satellite/SAT42811/Receiver/FU1_SFRX1		
            Satellite/SAT42811/Receiver/U1_SRX1		
            Satellite/SAT42811/Transmitter/D1_STX1		
            Satellite/SAT42811/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT42811/Receiver/FU1_SFRX1
            Satellite/SAT42811/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT42811/Receiver/U1_SRX1
            Satellite/SAT42811/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT42811/Transmitter/D1_STX1
            Satellite/SAT42811/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT42811/Transmitter/FD1_SFTX1
            Satellite/SAT42811/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT42812
            Satellite/SAT42812		
            Satellite/SAT42812/Receiver/FU1_SFRX1		
            Satellite/SAT42812/Receiver/U1_SRX1		
            Satellite/SAT42812/Transmitter/D1_STX1		
            Satellite/SAT42812/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT42812/Receiver/FU1_SFRX1
            Satellite/SAT42812/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT42812/Receiver/U1_SRX1
            Satellite/SAT42812/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT42812/Transmitter/D1_STX1
            Satellite/SAT42812/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT42812/Transmitter/FD1_SFTX1
            Satellite/SAT42812/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT42955
            Satellite/SAT42955		
            Satellite/SAT42955/Receiver/FU1_SFRX1		
            Satellite/SAT42955/Receiver/U1_SRX1		
            Satellite/SAT42955/Transmitter/D1_STX1		
            Satellite/SAT42955/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT42955/Receiver/FU1_SFRX1
            Satellite/SAT42955/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT42955/Receiver/U1_SRX1
            Satellite/SAT42955/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT42955/Transmitter/D1_STX1
            Satellite/SAT42955/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT42955/Transmitter/FD1_SFTX1
            Satellite/SAT42955/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT42956
            Satellite/SAT42956		
            Satellite/SAT42956/Receiver/FU1_SFRX1		
            Satellite/SAT42956/Receiver/U1_SRX1		
            Satellite/SAT42956/Transmitter/D1_STX1		
            Satellite/SAT42956/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT42956/Receiver/FU1_SFRX1
            Satellite/SAT42956/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT42956/Receiver/U1_SRX1
            Satellite/SAT42956/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT42956/Transmitter/D1_STX1
            Satellite/SAT42956/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT42956/Transmitter/FD1_SFTX1
            Satellite/SAT42956/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT42957
            Satellite/SAT42957		
            Satellite/SAT42957/Receiver/FU1_SFRX1		
            Satellite/SAT42957/Receiver/U1_SRX1		
            Satellite/SAT42957/Transmitter/D1_STX1		
            Satellite/SAT42957/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT42957/Receiver/FU1_SFRX1
            Satellite/SAT42957/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT42957/Receiver/U1_SRX1
            Satellite/SAT42957/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT42957/Transmitter/D1_STX1
            Satellite/SAT42957/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT42957/Transmitter/FD1_SFTX1
            Satellite/SAT42957/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT42958
            Satellite/SAT42958		
            Satellite/SAT42958/Receiver/FU1_SFRX1		
            Satellite/SAT42958/Receiver/U1_SRX1		
            Satellite/SAT42958/Transmitter/D1_STX1		
            Satellite/SAT42958/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT42958/Receiver/FU1_SFRX1
            Satellite/SAT42958/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT42958/Receiver/U1_SRX1
            Satellite/SAT42958/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT42958/Transmitter/D1_STX1
            Satellite/SAT42958/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT42958/Transmitter/FD1_SFTX1
            Satellite/SAT42958/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT42959
            Satellite/SAT42959		
            Satellite/SAT42959/Receiver/FU1_SFRX1		
            Satellite/SAT42959/Receiver/U1_SRX1		
            Satellite/SAT42959/Transmitter/D1_STX1		
            Satellite/SAT42959/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT42959/Receiver/FU1_SFRX1
            Satellite/SAT42959/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT42959/Receiver/U1_SRX1
            Satellite/SAT42959/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT42959/Transmitter/D1_STX1
            Satellite/SAT42959/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT42959/Transmitter/FD1_SFTX1
            Satellite/SAT42959/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT42960
            Satellite/SAT42960		
            Satellite/SAT42960/Receiver/FU1_SFRX1		
            Satellite/SAT42960/Receiver/U1_SRX1		
            Satellite/SAT42960/Transmitter/D1_STX1		
            Satellite/SAT42960/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT42960/Receiver/FU1_SFRX1
            Satellite/SAT42960/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT42960/Receiver/U1_SRX1
            Satellite/SAT42960/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT42960/Transmitter/D1_STX1
            Satellite/SAT42960/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT42960/Transmitter/FD1_SFTX1
            Satellite/SAT42960/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT42961
            Satellite/SAT42961		
            Satellite/SAT42961/Receiver/FU1_SFRX1		
            Satellite/SAT42961/Receiver/U1_SRX1		
            Satellite/SAT42961/Transmitter/D1_STX1		
            Satellite/SAT42961/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT42961/Receiver/FU1_SFRX1
            Satellite/SAT42961/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT42961/Receiver/U1_SRX1
            Satellite/SAT42961/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT42961/Transmitter/D1_STX1
            Satellite/SAT42961/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT42961/Transmitter/FD1_SFTX1
            Satellite/SAT42961/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT42962
            Satellite/SAT42962		
            Satellite/SAT42962/Receiver/FU1_SFRX1		
            Satellite/SAT42962/Receiver/U1_SRX1		
            Satellite/SAT42962/Transmitter/D1_STX1		
            Satellite/SAT42962/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT42962/Receiver/FU1_SFRX1
            Satellite/SAT42962/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT42962/Receiver/U1_SRX1
            Satellite/SAT42962/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT42962/Transmitter/D1_STX1
            Satellite/SAT42962/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT42962/Transmitter/FD1_SFTX1
            Satellite/SAT42962/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT42963
            Satellite/SAT42963		
            Satellite/SAT42963/Receiver/FU1_SFRX1		
            Satellite/SAT42963/Receiver/U1_SRX1		
            Satellite/SAT42963/Transmitter/D1_STX1		
            Satellite/SAT42963/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT42963/Receiver/FU1_SFRX1
            Satellite/SAT42963/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT42963/Receiver/U1_SRX1
            Satellite/SAT42963/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT42963/Transmitter/D1_STX1
            Satellite/SAT42963/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT42963/Transmitter/FD1_SFTX1
            Satellite/SAT42963/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT42964
            Satellite/SAT42964		
            Satellite/SAT42964/Receiver/FU1_SFRX1		
            Satellite/SAT42964/Receiver/U1_SRX1		
            Satellite/SAT42964/Transmitter/D1_STX1		
            Satellite/SAT42964/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT42964/Receiver/FU1_SFRX1
            Satellite/SAT42964/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT42964/Receiver/U1_SRX1
            Satellite/SAT42964/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT42964/Transmitter/D1_STX1
            Satellite/SAT42964/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT42964/Transmitter/FD1_SFTX1
            Satellite/SAT42964/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43070
            Satellite/SAT43070		
            Satellite/SAT43070/Receiver/FU1_SFRX1		
            Satellite/SAT43070/Receiver/U1_SRX1		
            Satellite/SAT43070/Transmitter/D1_STX1		
            Satellite/SAT43070/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43070/Receiver/FU1_SFRX1
            Satellite/SAT43070/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT43070/Receiver/U1_SRX1
            Satellite/SAT43070/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT43070/Transmitter/D1_STX1
            Satellite/SAT43070/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT43070/Transmitter/FD1_SFTX1
            Satellite/SAT43070/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43071
            Satellite/SAT43071		
            Satellite/SAT43071/Receiver/FU1_SFRX1		
            Satellite/SAT43071/Receiver/U1_SRX1		
            Satellite/SAT43071/Transmitter/D1_STX1		
            Satellite/SAT43071/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43071/Receiver/FU1_SFRX1
            Satellite/SAT43071/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT43071/Receiver/U1_SRX1
            Satellite/SAT43071/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT43071/Transmitter/D1_STX1
            Satellite/SAT43071/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT43071/Transmitter/FD1_SFTX1
            Satellite/SAT43071/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43072
            Satellite/SAT43072		
            Satellite/SAT43072/Receiver/FU1_SFRX1		
            Satellite/SAT43072/Receiver/U1_SRX1		
            Satellite/SAT43072/Transmitter/D1_STX1		
            Satellite/SAT43072/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43072/Receiver/FU1_SFRX1
            Satellite/SAT43072/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT43072/Receiver/U1_SRX1
            Satellite/SAT43072/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT43072/Transmitter/D1_STX1
            Satellite/SAT43072/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT43072/Transmitter/FD1_SFTX1
            Satellite/SAT43072/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43073
            Satellite/SAT43073		
            Satellite/SAT43073/Receiver/FU1_SFRX1		
            Satellite/SAT43073/Receiver/U1_SRX1		
            Satellite/SAT43073/Transmitter/D1_STX1		
            Satellite/SAT43073/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43073/Receiver/FU1_SFRX1
            Satellite/SAT43073/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT43073/Receiver/U1_SRX1
            Satellite/SAT43073/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT43073/Transmitter/D1_STX1
            Satellite/SAT43073/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT43073/Transmitter/FD1_SFTX1
            Satellite/SAT43073/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43074
            Satellite/SAT43074		
            Satellite/SAT43074/Receiver/FU1_SFRX1		
            Satellite/SAT43074/Receiver/U1_SRX1		
            Satellite/SAT43074/Transmitter/D1_STX1		
            Satellite/SAT43074/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43074/Receiver/FU1_SFRX1
            Satellite/SAT43074/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT43074/Receiver/U1_SRX1
            Satellite/SAT43074/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT43074/Transmitter/D1_STX1
            Satellite/SAT43074/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT43074/Transmitter/FD1_SFTX1
            Satellite/SAT43074/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43075
            Satellite/SAT43075		
            Satellite/SAT43075/Receiver/FU1_SFRX1		
            Satellite/SAT43075/Receiver/U1_SRX1		
            Satellite/SAT43075/Transmitter/D1_STX1		
            Satellite/SAT43075/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43075/Receiver/FU1_SFRX1
            Satellite/SAT43075/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT43075/Receiver/U1_SRX1
            Satellite/SAT43075/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT43075/Transmitter/D1_STX1
            Satellite/SAT43075/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT43075/Transmitter/FD1_SFTX1
            Satellite/SAT43075/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43076
            Satellite/SAT43076		
            Satellite/SAT43076/Receiver/FU1_SFRX1		
            Satellite/SAT43076/Receiver/U1_SRX1		
            Satellite/SAT43076/Transmitter/D1_STX1		
            Satellite/SAT43076/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43076/Receiver/FU1_SFRX1
            Satellite/SAT43076/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT43076/Receiver/U1_SRX1
            Satellite/SAT43076/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT43076/Transmitter/D1_STX1
            Satellite/SAT43076/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT43076/Transmitter/FD1_SFTX1
            Satellite/SAT43076/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43077
            Satellite/SAT43077		
            Satellite/SAT43077/Receiver/FU1_SFRX1		
            Satellite/SAT43077/Receiver/U1_SRX1		
            Satellite/SAT43077/Transmitter/D1_STX1		
            Satellite/SAT43077/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43077/Receiver/FU1_SFRX1
            Satellite/SAT43077/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT43077/Receiver/U1_SRX1
            Satellite/SAT43077/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT43077/Transmitter/D1_STX1
            Satellite/SAT43077/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT43077/Transmitter/FD1_SFTX1
            Satellite/SAT43077/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43078
            Satellite/SAT43078		
            Satellite/SAT43078/Receiver/FU1_SFRX1		
            Satellite/SAT43078/Receiver/U1_SRX1		
            Satellite/SAT43078/Transmitter/D1_STX1		
            Satellite/SAT43078/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43078/Receiver/FU1_SFRX1
            Satellite/SAT43078/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT43078/Receiver/U1_SRX1
            Satellite/SAT43078/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT43078/Transmitter/D1_STX1
            Satellite/SAT43078/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT43078/Transmitter/FD1_SFTX1
            Satellite/SAT43078/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43079
            Satellite/SAT43079		
            Satellite/SAT43079/Receiver/FU1_SFRX1		
            Satellite/SAT43079/Receiver/U1_SRX1		
            Satellite/SAT43079/Transmitter/D1_STX1		
            Satellite/SAT43079/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43079/Receiver/FU1_SFRX1
            Satellite/SAT43079/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT43079/Receiver/U1_SRX1
            Satellite/SAT43079/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT43079/Transmitter/D1_STX1
            Satellite/SAT43079/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT43079/Transmitter/FD1_SFTX1
            Satellite/SAT43079/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43249
            Satellite/SAT43249		
            Satellite/SAT43249/Receiver/FU1_SFRX1		
            Satellite/SAT43249/Receiver/U1_SRX1		
            Satellite/SAT43249/Transmitter/D1_STX1		
            Satellite/SAT43249/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43249/Receiver/FU1_SFRX1
            Satellite/SAT43249/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT43249/Receiver/U1_SRX1
            Satellite/SAT43249/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT43249/Transmitter/D1_STX1
            Satellite/SAT43249/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT43249/Transmitter/FD1_SFTX1
            Satellite/SAT43249/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43250
            Satellite/SAT43250		
            Satellite/SAT43250/Receiver/FU1_SFRX1		
            Satellite/SAT43250/Receiver/U1_SRX1		
            Satellite/SAT43250/Transmitter/D1_STX1		
            Satellite/SAT43250/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43250/Receiver/FU1_SFRX1
            Satellite/SAT43250/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT43250/Receiver/U1_SRX1
            Satellite/SAT43250/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT43250/Transmitter/D1_STX1
            Satellite/SAT43250/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT43250/Transmitter/FD1_SFTX1
            Satellite/SAT43250/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43251
            Satellite/SAT43251		
            Satellite/SAT43251/Receiver/FU1_SFRX1		
            Satellite/SAT43251/Receiver/U1_SRX1		
            Satellite/SAT43251/Transmitter/D1_STX1		
            Satellite/SAT43251/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43251/Receiver/FU1_SFRX1
            Satellite/SAT43251/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT43251/Receiver/U1_SRX1
            Satellite/SAT43251/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT43251/Transmitter/D1_STX1
            Satellite/SAT43251/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT43251/Transmitter/FD1_SFTX1
            Satellite/SAT43251/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43252
            Satellite/SAT43252		
            Satellite/SAT43252/Receiver/FU1_SFRX1		
            Satellite/SAT43252/Receiver/U1_SRX1		
            Satellite/SAT43252/Transmitter/D1_STX1		
            Satellite/SAT43252/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43252/Receiver/FU1_SFRX1
            Satellite/SAT43252/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT43252/Receiver/U1_SRX1
            Satellite/SAT43252/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT43252/Transmitter/D1_STX1
            Satellite/SAT43252/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT43252/Transmitter/FD1_SFTX1
            Satellite/SAT43252/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43253
            Satellite/SAT43253		
            Satellite/SAT43253/Receiver/FU1_SFRX1		
            Satellite/SAT43253/Receiver/U1_SRX1		
            Satellite/SAT43253/Transmitter/D1_STX1		
            Satellite/SAT43253/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43253/Receiver/FU1_SFRX1
            Satellite/SAT43253/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT43253/Receiver/U1_SRX1
            Satellite/SAT43253/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT43253/Transmitter/D1_STX1
            Satellite/SAT43253/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT43253/Transmitter/FD1_SFTX1
            Satellite/SAT43253/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43254
            Satellite/SAT43254		
            Satellite/SAT43254/Receiver/FU1_SFRX1		
            Satellite/SAT43254/Receiver/U1_SRX1		
            Satellite/SAT43254/Transmitter/D1_STX1		
            Satellite/SAT43254/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43254/Receiver/FU1_SFRX1
            Satellite/SAT43254/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT43254/Receiver/U1_SRX1
            Satellite/SAT43254/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT43254/Transmitter/D1_STX1
            Satellite/SAT43254/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT43254/Transmitter/FD1_SFTX1
            Satellite/SAT43254/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43255
            Satellite/SAT43255		
            Satellite/SAT43255/Receiver/FU1_SFRX1		
            Satellite/SAT43255/Receiver/U1_SRX1		
            Satellite/SAT43255/Transmitter/D1_STX1		
            Satellite/SAT43255/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43255/Receiver/FU1_SFRX1
            Satellite/SAT43255/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT43255/Receiver/U1_SRX1
            Satellite/SAT43255/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT43255/Transmitter/D1_STX1
            Satellite/SAT43255/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT43255/Transmitter/FD1_SFTX1
            Satellite/SAT43255/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43256
            Satellite/SAT43256		
            Satellite/SAT43256/Receiver/FU1_SFRX1		
            Satellite/SAT43256/Receiver/U1_SRX1		
            Satellite/SAT43256/Transmitter/D1_STX1		
            Satellite/SAT43256/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43256/Receiver/FU1_SFRX1
            Satellite/SAT43256/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT43256/Receiver/U1_SRX1
            Satellite/SAT43256/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT43256/Transmitter/D1_STX1
            Satellite/SAT43256/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT43256/Transmitter/FD1_SFTX1
            Satellite/SAT43256/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43257
            Satellite/SAT43257		
            Satellite/SAT43257/Receiver/FU1_SFRX1		
            Satellite/SAT43257/Receiver/U1_SRX1		
            Satellite/SAT43257/Transmitter/D1_STX1		
            Satellite/SAT43257/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43257/Receiver/FU1_SFRX1
            Satellite/SAT43257/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT43257/Receiver/U1_SRX1
            Satellite/SAT43257/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT43257/Transmitter/D1_STX1
            Satellite/SAT43257/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT43257/Transmitter/FD1_SFTX1
            Satellite/SAT43257/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43258
            Satellite/SAT43258		
            Satellite/SAT43258/Receiver/FU1_SFRX1		
            Satellite/SAT43258/Receiver/U1_SRX1		
            Satellite/SAT43258/Transmitter/D1_STX1		
            Satellite/SAT43258/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43258/Receiver/FU1_SFRX1
            Satellite/SAT43258/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT43258/Receiver/U1_SRX1
            Satellite/SAT43258/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT43258/Transmitter/D1_STX1
            Satellite/SAT43258/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT43258/Transmitter/FD1_SFTX1
            Satellite/SAT43258/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43478
            Satellite/SAT43478		
            Satellite/SAT43478/Receiver/FU1_SFRX1		
            Satellite/SAT43478/Receiver/U1_SRX1		
            Satellite/SAT43478/Transmitter/D1_STX1		
            Satellite/SAT43478/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43478/Receiver/FU1_SFRX1
            Satellite/SAT43478/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT43478/Receiver/U1_SRX1
            Satellite/SAT43478/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT43478/Transmitter/D1_STX1
            Satellite/SAT43478/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT43478/Transmitter/FD1_SFTX1
            Satellite/SAT43478/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43479
            Satellite/SAT43479		
            Satellite/SAT43479/Receiver/FU1_SFRX1		
            Satellite/SAT43479/Receiver/U1_SRX1		
            Satellite/SAT43479/Transmitter/D1_STX1		
            Satellite/SAT43479/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43479/Receiver/FU1_SFRX1
            Satellite/SAT43479/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT43479/Receiver/U1_SRX1
            Satellite/SAT43479/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT43479/Transmitter/D1_STX1
            Satellite/SAT43479/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT43479/Transmitter/FD1_SFTX1
            Satellite/SAT43479/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43480
            Satellite/SAT43480		
            Satellite/SAT43480/Receiver/FU1_SFRX1		
            Satellite/SAT43480/Receiver/U1_SRX1		
            Satellite/SAT43480/Transmitter/D1_STX1		
            Satellite/SAT43480/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43480/Receiver/FU1_SFRX1
            Satellite/SAT43480/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT43480/Receiver/U1_SRX1
            Satellite/SAT43480/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT43480/Transmitter/D1_STX1
            Satellite/SAT43480/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT43480/Transmitter/FD1_SFTX1
            Satellite/SAT43480/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43481
            Satellite/SAT43481		
            Satellite/SAT43481/Receiver/FU1_SFRX1		
            Satellite/SAT43481/Receiver/U1_SRX1		
            Satellite/SAT43481/Transmitter/D1_STX1		
            Satellite/SAT43481/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43481/Receiver/FU1_SFRX1
            Satellite/SAT43481/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT43481/Receiver/U1_SRX1
            Satellite/SAT43481/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT43481/Transmitter/D1_STX1
            Satellite/SAT43481/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT43481/Transmitter/FD1_SFTX1
            Satellite/SAT43481/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43482
            Satellite/SAT43482		
            Satellite/SAT43482/Receiver/FU1_SFRX1		
            Satellite/SAT43482/Receiver/U1_SRX1		
            Satellite/SAT43482/Transmitter/D1_STX1		
            Satellite/SAT43482/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43482/Receiver/FU1_SFRX1
            Satellite/SAT43482/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT43482/Receiver/U1_SRX1
            Satellite/SAT43482/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT43482/Transmitter/D1_STX1
            Satellite/SAT43482/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT43482/Transmitter/FD1_SFTX1
            Satellite/SAT43482/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43569
            Satellite/SAT43569		
            Satellite/SAT43569/Receiver/FU1_SFRX1		
            Satellite/SAT43569/Receiver/U1_SRX1		
            Satellite/SAT43569/Transmitter/D1_STX1		
            Satellite/SAT43569/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43569/Receiver/FU1_SFRX1
            Satellite/SAT43569/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT43569/Receiver/U1_SRX1
            Satellite/SAT43569/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT43569/Transmitter/D1_STX1
            Satellite/SAT43569/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT43569/Transmitter/FD1_SFTX1
            Satellite/SAT43569/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43570
            Satellite/SAT43570		
            Satellite/SAT43570/Receiver/FU1_SFRX1		
            Satellite/SAT43570/Receiver/U1_SRX1		
            Satellite/SAT43570/Transmitter/D1_STX1		
            Satellite/SAT43570/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43570/Receiver/FU1_SFRX1
            Satellite/SAT43570/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT43570/Receiver/U1_SRX1
            Satellite/SAT43570/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT43570/Transmitter/D1_STX1
            Satellite/SAT43570/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT43570/Transmitter/FD1_SFTX1
            Satellite/SAT43570/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43571
            Satellite/SAT43571		
            Satellite/SAT43571/Receiver/FU1_SFRX1		
            Satellite/SAT43571/Receiver/U1_SRX1		
            Satellite/SAT43571/Transmitter/D1_STX1		
            Satellite/SAT43571/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43571/Receiver/FU1_SFRX1
            Satellite/SAT43571/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT43571/Receiver/U1_SRX1
            Satellite/SAT43571/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT43571/Transmitter/D1_STX1
            Satellite/SAT43571/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT43571/Transmitter/FD1_SFTX1
            Satellite/SAT43571/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43572
            Satellite/SAT43572		
            Satellite/SAT43572/Receiver/FU1_SFRX1		
            Satellite/SAT43572/Receiver/U1_SRX1		
            Satellite/SAT43572/Transmitter/D1_STX1		
            Satellite/SAT43572/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43572/Receiver/FU1_SFRX1
            Satellite/SAT43572/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT43572/Receiver/U1_SRX1
            Satellite/SAT43572/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT43572/Transmitter/D1_STX1
            Satellite/SAT43572/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT43572/Transmitter/FD1_SFTX1
            Satellite/SAT43572/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43573
            Satellite/SAT43573		
            Satellite/SAT43573/Receiver/FU1_SFRX1		
            Satellite/SAT43573/Receiver/U1_SRX1		
            Satellite/SAT43573/Transmitter/D1_STX1		
            Satellite/SAT43573/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43573/Receiver/FU1_SFRX1
            Satellite/SAT43573/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT43573/Receiver/U1_SRX1
            Satellite/SAT43573/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT43573/Transmitter/D1_STX1
            Satellite/SAT43573/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT43573/Transmitter/FD1_SFTX1
            Satellite/SAT43573/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43574
            Satellite/SAT43574		
            Satellite/SAT43574/Receiver/FU1_SFRX1		
            Satellite/SAT43574/Receiver/U1_SRX1		
            Satellite/SAT43574/Transmitter/D1_STX1		
            Satellite/SAT43574/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43574/Receiver/FU1_SFRX1
            Satellite/SAT43574/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT43574/Receiver/U1_SRX1
            Satellite/SAT43574/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT43574/Transmitter/D1_STX1
            Satellite/SAT43574/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT43574/Transmitter/FD1_SFTX1
            Satellite/SAT43574/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43575
            Satellite/SAT43575		
            Satellite/SAT43575/Receiver/FU1_SFRX1		
            Satellite/SAT43575/Receiver/U1_SRX1		
            Satellite/SAT43575/Transmitter/D1_STX1		
            Satellite/SAT43575/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43575/Receiver/FU1_SFRX1
            Satellite/SAT43575/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT43575/Receiver/U1_SRX1
            Satellite/SAT43575/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT43575/Transmitter/D1_STX1
            Satellite/SAT43575/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT43575/Transmitter/FD1_SFTX1
            Satellite/SAT43575/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43576
            Satellite/SAT43576		
            Satellite/SAT43576/Receiver/FU1_SFRX1		
            Satellite/SAT43576/Receiver/U1_SRX1		
            Satellite/SAT43576/Transmitter/D1_STX1		
            Satellite/SAT43576/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43576/Receiver/FU1_SFRX1
            Satellite/SAT43576/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT43576/Receiver/U1_SRX1
            Satellite/SAT43576/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT43576/Transmitter/D1_STX1
            Satellite/SAT43576/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT43576/Transmitter/FD1_SFTX1
            Satellite/SAT43576/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43577
            Satellite/SAT43577		
            Satellite/SAT43577/Receiver/FU1_SFRX1		
            Satellite/SAT43577/Receiver/U1_SRX1		
            Satellite/SAT43577/Transmitter/D1_STX1		
            Satellite/SAT43577/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43577/Receiver/FU1_SFRX1
            Satellite/SAT43577/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT43577/Receiver/U1_SRX1
            Satellite/SAT43577/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT43577/Transmitter/D1_STX1
            Satellite/SAT43577/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT43577/Transmitter/FD1_SFTX1
            Satellite/SAT43577/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43578
            Satellite/SAT43578		
            Satellite/SAT43578/Receiver/FU1_SFRX1		
            Satellite/SAT43578/Receiver/U1_SRX1		
            Satellite/SAT43578/Transmitter/D1_STX1		
            Satellite/SAT43578/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43578/Receiver/FU1_SFRX1
            Satellite/SAT43578/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT43578/Receiver/U1_SRX1
            Satellite/SAT43578/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT43578/Transmitter/D1_STX1
            Satellite/SAT43578/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT43578/Transmitter/FD1_SFTX1
            Satellite/SAT43578/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43922
            Satellite/SAT43922		
            Satellite/SAT43922/Receiver/FU1_SFRX1		
            Satellite/SAT43922/Receiver/U1_SRX1		
            Satellite/SAT43922/Transmitter/D1_STX1		
            Satellite/SAT43922/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43922/Receiver/FU1_SFRX1
            Satellite/SAT43922/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT43922/Receiver/U1_SRX1
            Satellite/SAT43922/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT43922/Transmitter/D1_STX1
            Satellite/SAT43922/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT43922/Transmitter/FD1_SFTX1
            Satellite/SAT43922/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43923
            Satellite/SAT43923		
            Satellite/SAT43923/Receiver/FU1_SFRX1		
            Satellite/SAT43923/Receiver/U1_SRX1		
            Satellite/SAT43923/Transmitter/D1_STX1		
            Satellite/SAT43923/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43923/Receiver/FU1_SFRX1
            Satellite/SAT43923/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT43923/Receiver/U1_SRX1
            Satellite/SAT43923/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT43923/Transmitter/D1_STX1
            Satellite/SAT43923/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT43923/Transmitter/FD1_SFTX1
            Satellite/SAT43923/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43924
            Satellite/SAT43924		
            Satellite/SAT43924/Receiver/FU1_SFRX1		
            Satellite/SAT43924/Receiver/U1_SRX1		
            Satellite/SAT43924/Transmitter/D1_STX1		
            Satellite/SAT43924/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43924/Receiver/FU1_SFRX1
            Satellite/SAT43924/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT43924/Receiver/U1_SRX1
            Satellite/SAT43924/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT43924/Transmitter/D1_STX1
            Satellite/SAT43924/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT43924/Transmitter/FD1_SFTX1
            Satellite/SAT43924/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43925
            Satellite/SAT43925		
            Satellite/SAT43925/Receiver/FU1_SFRX1		
            Satellite/SAT43925/Receiver/U1_SRX1		
            Satellite/SAT43925/Transmitter/D1_STX1		
            Satellite/SAT43925/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43925/Receiver/FU1_SFRX1
            Satellite/SAT43925/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT43925/Receiver/U1_SRX1
            Satellite/SAT43925/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT43925/Transmitter/D1_STX1
            Satellite/SAT43925/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT43925/Transmitter/FD1_SFTX1
            Satellite/SAT43925/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43926
            Satellite/SAT43926		
            Satellite/SAT43926/Receiver/FU1_SFRX1		
            Satellite/SAT43926/Receiver/U1_SRX1		
            Satellite/SAT43926/Transmitter/D1_STX1		
            Satellite/SAT43926/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43926/Receiver/FU1_SFRX1
            Satellite/SAT43926/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT43926/Receiver/U1_SRX1
            Satellite/SAT43926/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT43926/Transmitter/D1_STX1
            Satellite/SAT43926/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT43926/Transmitter/FD1_SFTX1
            Satellite/SAT43926/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43927
            Satellite/SAT43927		
            Satellite/SAT43927/Receiver/FU1_SFRX1		
            Satellite/SAT43927/Receiver/U1_SRX1		
            Satellite/SAT43927/Transmitter/D1_STX1		
            Satellite/SAT43927/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43927/Receiver/FU1_SFRX1
            Satellite/SAT43927/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT43927/Receiver/U1_SRX1
            Satellite/SAT43927/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT43927/Transmitter/D1_STX1
            Satellite/SAT43927/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT43927/Transmitter/FD1_SFTX1
            Satellite/SAT43927/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43928
            Satellite/SAT43928		
            Satellite/SAT43928/Receiver/FU1_SFRX1		
            Satellite/SAT43928/Receiver/U1_SRX1		
            Satellite/SAT43928/Transmitter/D1_STX1		
            Satellite/SAT43928/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43928/Receiver/FU1_SFRX1
            Satellite/SAT43928/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT43928/Receiver/U1_SRX1
            Satellite/SAT43928/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT43928/Transmitter/D1_STX1
            Satellite/SAT43928/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT43928/Transmitter/FD1_SFTX1
            Satellite/SAT43928/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43929
            Satellite/SAT43929		
            Satellite/SAT43929/Receiver/FU1_SFRX1		
            Satellite/SAT43929/Receiver/U1_SRX1		
            Satellite/SAT43929/Transmitter/D1_STX1		
            Satellite/SAT43929/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43929/Receiver/FU1_SFRX1
            Satellite/SAT43929/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT43929/Receiver/U1_SRX1
            Satellite/SAT43929/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT43929/Transmitter/D1_STX1
            Satellite/SAT43929/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT43929/Transmitter/FD1_SFTX1
            Satellite/SAT43929/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43930
            Satellite/SAT43930		
            Satellite/SAT43930/Receiver/FU1_SFRX1		
            Satellite/SAT43930/Receiver/U1_SRX1		
            Satellite/SAT43930/Transmitter/D1_STX1		
            Satellite/SAT43930/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43930/Receiver/FU1_SFRX1
            Satellite/SAT43930/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT43930/Receiver/U1_SRX1
            Satellite/SAT43930/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT43930/Transmitter/D1_STX1
            Satellite/SAT43930/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT43930/Transmitter/FD1_SFTX1
            Satellite/SAT43930/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43931
            Satellite/SAT43931		
            Satellite/SAT43931/Receiver/FU1_SFRX1		
            Satellite/SAT43931/Receiver/U1_SRX1		
            Satellite/SAT43931/Transmitter/D1_STX1		
            Satellite/SAT43931/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT43931/Receiver/FU1_SFRX1
            Satellite/SAT43931/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT43931/Receiver/U1_SRX1
            Satellite/SAT43931/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT43931/Transmitter/D1_STX1
            Satellite/SAT43931/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT43931/Transmitter/FD1_SFTX1
            Satellite/SAT43931/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT56726
            Satellite/SAT56726		
            Satellite/SAT56726/Receiver/FU1_SFRX1		
            Satellite/SAT56726/Receiver/U1_SRX1		
            Satellite/SAT56726/Transmitter/D1_STX1		
            Satellite/SAT56726/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT56726/Receiver/FU1_SFRX1
            Satellite/SAT56726/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT56726/Receiver/U1_SRX1
            Satellite/SAT56726/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT56726/Transmitter/D1_STX1
            Satellite/SAT56726/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT56726/Transmitter/FD1_SFTX1
            Satellite/SAT56726/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT56727
            Satellite/SAT56727		
            Satellite/SAT56727/Receiver/FU1_SFRX1		
            Satellite/SAT56727/Receiver/U1_SRX1		
            Satellite/SAT56727/Transmitter/D1_STX1		
            Satellite/SAT56727/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT56727/Receiver/FU1_SFRX1
            Satellite/SAT56727/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT56727/Receiver/U1_SRX1
            Satellite/SAT56727/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT56727/Transmitter/D1_STX1
            Satellite/SAT56727/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT56727/Transmitter/FD1_SFTX1
            Satellite/SAT56727/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT56728
            Satellite/SAT56728		
            Satellite/SAT56728/Receiver/FU1_SFRX1		
            Satellite/SAT56728/Receiver/U1_SRX1		
            Satellite/SAT56728/Transmitter/D1_STX1		
            Satellite/SAT56728/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT56728/Receiver/FU1_SFRX1
            Satellite/SAT56728/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT56728/Receiver/U1_SRX1
            Satellite/SAT56728/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT56728/Transmitter/D1_STX1
            Satellite/SAT56728/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT56728/Transmitter/FD1_SFTX1
            Satellite/SAT56728/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT56729
            Satellite/SAT56729		
            Satellite/SAT56729/Receiver/FU1_SFRX1		
            Satellite/SAT56729/Receiver/U1_SRX1		
            Satellite/SAT56729/Transmitter/D1_STX1		
            Satellite/SAT56729/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT56729/Receiver/FU1_SFRX1
            Satellite/SAT56729/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT56729/Receiver/U1_SRX1
            Satellite/SAT56729/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT56729/Transmitter/D1_STX1
            Satellite/SAT56729/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT56729/Transmitter/FD1_SFTX1
            Satellite/SAT56729/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT56730
            Satellite/SAT56730		
            Satellite/SAT56730/Receiver/FU1_SFRX1		
            Satellite/SAT56730/Receiver/U1_SRX1		
            Satellite/SAT56730/Transmitter/D1_STX1		
            Satellite/SAT56730/Transmitter/FD1_SFTX1		
        END Instance
        Instance Satellite/SAT56730/Receiver/FU1_SFRX1
            Satellite/SAT56730/Receiver/FU1_SFRX1		
        END Instance
        Instance Satellite/SAT56730/Receiver/U1_SRX1
            Satellite/SAT56730/Receiver/U1_SRX1		
        END Instance
        Instance Satellite/SAT56730/Transmitter/D1_STX1
            Satellite/SAT56730/Transmitter/D1_STX1		
        END Instance
        Instance Satellite/SAT56730/Transmitter/FD1_SFTX1
            Satellite/SAT56730/Transmitter/FD1_SFTX1		
        END Instance
    END References

END Scenario
