# Requirements Document

## Introduction

This document specifies the requirements for a modern V2Ray client application for Ubuntu. The system enables users to manage V2Ray server subscriptions, connect to VPN servers with a single click, and monitor connection status through a colorful, modern graphical interface. The application includes comprehensive automated testing to ensure reliability and correctness of both GUI and V2Ray functionality.

## Glossary

- **V2Ray Client**: The desktop application that manages V2Ray connections
- **V2Ray Core**: The underlying V2Ray/XRay binary that handles VPN connections
- **Subscription Link**: A URL pointing to a list of V2Ray server configurations
- **Server Configuration**: JSON data defining a V2Ray server's connection parameters
- **Connection Manager**: The component responsible for starting and stopping V2Ray processes
- **Subscription Manager**: The component that fetches and decodes server lists from URLs
- **GUI**: The PyQt6-based graphical user interface
- **Server Card**: A visual UI element displaying server information with flags and ping data

## Requirements

### Requirement 1: Subscription Management

**User Story:** As a user, I want to add multiple subscription URLs so that I can access servers from different providers

#### Acceptance Criteria

1. WHEN the user adds a subscription URL, THE Subscription Manager SHALL fetch the content from the URL and decode any Base64-encoded data
2. THE Subscription Manager SHALL support GitHub raw URLs, .txt files, .json files, and .v2ray format files
3. WHEN multiple subscriptions contain duplicate servers, THE Subscription Manager SHALL merge them into a single list without duplicates
4. THE GUI SHALL provide buttons to add, edit, and remove subscription URLs
5. WHEN the user clicks the refresh button, THE Subscription Manager SHALL fetch updated server lists from all configured subscription URLs

### Requirement 2: Automatic Server Updates

**User Story:** As a user, I want the server list to update automatically so that I always have access to the latest working servers

#### Acceptance Criteria

1. THE Server Updater SHALL refresh all subscription links every 10 seconds by default
2. WHERE the user configures a custom refresh interval, THE Server Updater SHALL use the user-specified interval
3. WHEN a subscription fetch fails, THE Server Updater SHALL log the error and continue with other subscriptions
4. THE Server Updater SHALL update the server list in the GUI without interrupting an active connection

### Requirement 3: Server Connection

**User Story:** As a user, I want to connect to a V2Ray server with a single click so that I can quickly establish a VPN connection

#### Acceptance Criteria

1. WHEN the user clicks connect on a server, THE Connection Manager SHALL save the server configuration to ~/.config/v2ray-client/temp_config.json
2. THE Connection Manager SHALL start the V2Ray Core process with the temporary configuration file
3. WHEN the V2Ray Core process starts successfully, THE GUI SHALL display connection status as "Connected" with a green indicator
4. THE Connection Manager SHALL fetch and display the current public IP address from https://ipinfo.io
5. THE GUI SHALL display the connected server name and ping latency

### Requirement 4: Server Disconnection

**User Story:** As a user, I want to disconnect from the VPN with a single click so that I can quickly restore my normal internet connection

#### Acceptance Criteria

1. WHEN the user clicks disconnect, THE Connection Manager SHALL terminate the V2Ray Core process
2. THE Connection Manager SHALL delete the temporary configuration file
3. WHEN disconnection completes, THE GUI SHALL update the status to "Disconnected" with a red indicator
4. THE Connection Manager SHALL clear the displayed IP address and server information

### Requirement 5: Modern Graphical Interface

**User Story:** As a user, I want a visually appealing and intuitive interface so that the application is pleasant to use

#### Acceptance Criteria

1. THE GUI SHALL be built using PyQt6 framework
2. THE GUI SHALL include three tabs: Servers, Settings, and Logs
3. THE GUI SHALL use neon gradients with purple, blue, and cyan colors
4. THE GUI SHALL display server cards with rounded corners and shadow effects
5. WHEN the user hovers over buttons, THE GUI SHALL display animated glow effects
6. THE GUI SHALL display country flags on server cards
7. THE GUI SHALL display ping latency as visual bars or indicators

### Requirement 6: Theme Customization

**User Story:** As a user, I want to choose between different visual themes so that I can customize the appearance to my preference

#### Acceptance Criteria

1. THE GUI SHALL support Dark, Neon, and Light theme modes
2. WHEN the user selects a theme in Settings, THE GUI SHALL apply the theme immediately
3. THE GUI SHALL persist the selected theme across application restarts

### Requirement 7: Live Log Monitoring

**User Story:** As a user, I want to view live V2Ray logs so that I can troubleshoot connection issues

#### Acceptance Criteria

1. THE GUI SHALL display a Logs tab with a scrollable text area
2. WHILE the V2Ray Core process is running, THE GUI SHALL stream stdout and stderr to the Logs tab
3. THE GUI SHALL automatically scroll to the newest log entries
4. THE GUI SHALL retain log history until the application is closed

### Requirement 8: Settings Management

**User Story:** As a user, I want to configure application settings so that I can customize behavior to my needs

#### Acceptance Criteria

1. THE GUI SHALL provide a Settings tab with configuration options
2. THE Settings tab SHALL allow users to set the refresh interval with a minimum of 5 seconds
3. THE Settings tab SHALL allow users to select the visual theme
4. THE Settings tab SHALL display the list of configured subscription URLs
5. THE Settings tab SHALL provide an option to enable auto-start on login

### Requirement 9: Server Information Display

**User Story:** As a user, I want to see detailed information about each server so that I can choose the best one for my needs

#### Acceptance Criteria

1. THE GUI SHALL display server name, country flag, IP address, and port for each server
2. THE GUI SHALL display ping latency for each server
3. THE GUI SHALL update ping information periodically
4. THE GUI SHALL sort servers by ping latency or alphabetically based on user preference

### Requirement 10: Visual Feedback

**User Story:** As a user, I want clear visual feedback for my actions so that I know when operations succeed or fail

#### Acceptance Criteria

1. WHEN a user action completes successfully, THE GUI SHALL display a toast notification with a success message
2. WHEN a user action fails, THE GUI SHALL display a toast notification with an error message
3. WHEN connecting to a server, THE GUI SHALL animate the connect button with a color transition from red to green
4. THE GUI SHALL display animated indicators during loading operations

### Requirement 11: Automated GUI Testing

**User Story:** As a developer, I want automated GUI tests so that I can verify the interface works correctly

#### Acceptance Criteria

1. THE test suite SHALL include tests that launch the GUI and verify all tabs are accessible
2. THE test suite SHALL verify that all buttons respond to clicks
3. THE test suite SHALL verify tab navigation works correctly
4. THE test suite SHALL run using the pytest framework
5. THE test suite SHALL complete GUI tests within 10 seconds

### Requirement 12: Automated V2Ray Process Testing

**User Story:** As a developer, I want automated tests for V2Ray process management so that I can ensure connection reliability

#### Acceptance Criteria

1. THE test suite SHALL verify that the Connection Manager can start a V2Ray process
2. THE test suite SHALL verify that the Connection Manager can stop a V2Ray process cleanly
3. THE test suite SHALL verify that temporary configuration files are created and deleted correctly
4. THE test suite SHALL verify that connection status updates correctly
5. THE test suite SHALL use mock V2Ray processes to avoid requiring actual V2Ray installation during testing

### Requirement 13: Automated Subscription Testing

**User Story:** As a developer, I want automated tests for subscription management so that I can ensure server lists are parsed correctly

#### Acceptance Criteria

1. THE test suite SHALL verify that the Subscription Manager can fetch content from URLs
2. THE test suite SHALL verify that Base64-encoded .v2ray links are decoded correctly
3. THE test suite SHALL verify that JSON server configurations are parsed correctly
4. THE test suite SHALL verify that duplicate servers are removed during merging
5. THE test suite SHALL use mock HTTP responses to avoid network dependencies during testing

### Requirement 14: Automated Network Testing

**User Story:** As a developer, I want automated tests for network functionality so that I can ensure connectivity features work correctly

#### Acceptance Criteria

1. THE test suite SHALL verify that ping measurements work correctly
2. THE test suite SHALL verify that IP address fetching from ipinfo.io works correctly
3. THE test suite SHALL verify that refresh intervals are respected
4. THE test suite SHALL verify that JSON schema validation works for server configurations
5. THE test suite SHALL handle network failures gracefully during testing

### Requirement 15: Installation and Setup

**User Story:** As a user, I want a simple installation process so that I can quickly set up the application

#### Acceptance Criteria

1. THE installation script SHALL install Python 3 and pip if not present
2. THE installation script SHALL install PyQt6, requests, and pytest packages
3. THE installation script SHALL install V2Ray Core using the official installation script
4. THE installation script SHALL create necessary configuration directories
5. THE installation script SHALL be executable on Ubuntu 20.04 and later versions

### Requirement 16: Package Distribution

**User Story:** As a user, I want to install the application using a standard package format so that installation is convenient

#### Acceptance Criteria

1. THE project SHALL provide a .deb package for Debian-based distributions
2. THE project SHALL provide an .AppImage package for universal Linux compatibility
3. THE packages SHALL include all necessary dependencies except V2Ray Core
4. THE packages SHALL create desktop menu entries with application icons
