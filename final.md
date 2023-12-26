# Ankita Task

## Breakdown

### Electron App Execution Initiating Python Script

 1. The Electron app needs to be configured to execute a Python script upon launch.
 2. This Python script will start a WebSocket server.

### Python Script Sending Server Credentials

1. Once the WebSocket server is running, the Python script should send server credentials (such as IP address, port, and any necessary authentication information) to the Electron app.

### Electron App Waiting and Connecting to the Server

1. The Electron app must be programmed to wait for these credentials.
2. After receiving the credentials, the Electron app should establish a connection with the WebSocket server using these details.

### Enabling/Disabling Keyboard Functionality in Electron App

1. Implement a button in the Electron app's which appear after connection with server is established.
2. This button will control the enabling and disabling of the keyboard(it send request to server to enable keyboard blocking and unblocking).

## Technical Help

### Electron & Python Integration

 1. Use Node.js's child_process module in the Electron app to spawn the Python script.
 2. Handle standard output (stdout) in Electron to receive data from the Python script.
