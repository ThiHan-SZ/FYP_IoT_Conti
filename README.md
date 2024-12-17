<h1 align="center">Final Year Project</h1>

<p align="center">Development of a Simulator for Wireless Communications</p>

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Contact](#contact)

## Introduction

#### Hardware development
- You can find the related hardware resources in the [FYP_NextGenIoT_Hardware](../main/FYP_NextGenIoT_Hardware) folder
- The hardware development section is a re-establishment of the previous project from AY24/25 April

#### Software development
- You can find the related hardware resources in the [FYP_NextGenIoT_Simulator](../main/FYP_NextGenIoT_Simulator) folder
- The simulator folder contains :

| Folders  | Description               |
| ------------- | :--------------------------- |
| [Archive](../main/FYP_NextGenIoT_Simulator/Archive)   | An archive of deprecated code|
| [QAM Generators](../main/FYP_NextGenIoT_Simulator/QAM_Generators) | Generator Code for QAM Constellation LUTs            |
| [QAM LUT pkl](../main/FYP_NextGenIoT_Simulator/QAM_LUT_pkl) | Directory to store all QAM LUTs |
| [Simulation Class CLI](../main/FYP_NextGenIoT_Simulator/Simulator/SimulationClassCLI) | CLI variant of simulator - Standalone CLI app |
| [Simulation Class Compact](../main/FYP_NextGenIoT_Simulator/Simulator/SimulationClassCompact) | Compact variant of simulator - Import into projects |
| [Testcase Files](../main/FYP_NextGenIoT_Simulator/TestcaseFiles) | Test Case .txt files containing some test strings |
| [Test Environment](../main/FYP_NextGenIoT_Simulator/TestEnv)  | Directory containing test scripts |
| [Wave Files](../main/FYP_NextGenIoT_Simulator/WaveFiles) | Directory to store all generated .wav files |

- The direcotry contains the simulator and various scripts and test files used to create and test the simulator

## Features

#### Modulator
- The simulator contains a dynamic modulator that takes in the carrier frequency, bit rate and modulations scheme to generate a modulated transmission signal

#### Demodulator
- The simulator contains a demodulator that takes in the a wave file, bit rate and modulations scheme to generate a modulated transmission signal

## Contact

This project was developed by Thi Han Soe Zaw and Wan Yan Kai in AY24/25 October w/ Continental Singapore
