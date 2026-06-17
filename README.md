#  WasteFlow  — Healthcare Waste Management System

##  Overview

**WasteFlow Health** is a healthcare waste management system developed for Uganda Christian University's Intensive Recess Bootcamp 2026. The system tracks, monitors, and manages the disposal of healthcare waste using ultrasonic sensors and a web-based platform.

The system addresses critical challenges in healthcare waste management, including:
- Real-time monitoring of bin fill levels
- Efficient waste collection route planning
- Regulatory compliance reporting
- Segregation of infectious, sharps, pharmaceutical, and general waste

## Technology Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | React.js |
| **Backend** | Express.js (Node.js) |
| **Database** | MySQL |
| **Hardware** | Ultrasonic sensors (HC-SR04), ESP8266/ESP32 microcontrollers |
| **Version Control** | Git and GitHub |
| **Project Management** | Agile (Scrum) with GitHub Projects |

##  System Features

### User Roles

| Role | Responsibilities |
|------|------------------|
| **System Administrator** | User management, system configuration, audit logs, compliance reporting |
| **Facility Manager** | Bin status dashboard, collection scheduling, waste generation reports |
| **Waste Personnel** | Route viewing, QR code scanning, bin emptying confirmation |

### Core Functionality

- **Real-time Bin Monitoring:** Ultrasonic sensors measure fill levels and transmit data to the server
- **Automated Alerts:** Notifications when bins exceed configured thresholds
- **Collection Route Optimization:** Schedule and assign collection routes for waste personnel
- **Compliance Reporting:** Generate reports for regulatory submissions
- **Audit Trail:** Track all user actions for accountability

### Hardware Components

- **Ultrasonic Sensors (HC-SR04):** Mounted on bin lids, measure distance to waste surface
- **Microcontrollers (ESP8266/ESP32):** Process sensor data and transmit to server
- **QR Code Labels:** Unique identifiers for each bin
- **Mobile Devices:** Waste personnel use smartphones to scan QR codes and update status

##  Entity Relationship Diagram

The database consists of the following entities:
**User ⟷ Role**
**Facility ⟷ Department ⟷ Staff**
**Facility ⟷ Bin ⟷ Collection**
**Bin ⟷ Sensor_Readings**
**Bin ⟷ Notifications**
**Bin ⟷ Qualifications**
**Collection ⟷ Disposal_Records**
**User ⟷ Audit_Logs**

Team Members
| Name | Role |
|------|------|
| **Lisa Kushaba** | Scrum master |
| **Mr. Tony Kisomose** |  Product Owner |
| **Job Komakech** | Backend Developer |
| **Mercy Akankunda** | Frontend Developer |
| **Emmanuel Ainomugisha** | QA Tester |
| **Gerald Junior Okware** | Documentation Lead |
