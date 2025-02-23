# INTELMONITOR-DASHBOARD

## Overview

This is a web-based real-time monitoring dashboard designed to provide a clear and insightful overview of key metrics. It's built using web technologies and leverages Socket.IO for real-time data updates, Chart.js for interactive charts, and Leaflet for map visualizations.

Currently, it monitors:

*   **People Flow:** Tracks people entering (IN) and leaving (OUT) a space.
*   **Storage Usage:** Displays storage utilization with progress bars and detailed metrics.
*   **Temperature:** Shows real-time temperature readings.
*   **Location Tracking:** Pinpoints location on a map and displays coordinates.
*   **Speed:** Visualizes speed using a dynamic speedometer.
*   **Weather:** Updating.
  
![web](images/web_new.png)

*Figure 1: INTELMONITOR-DASHBOARD*

The dashboard shown as Figure 1 is designed to be responsive, ensuring optimal viewing on various devices, specially optimized for low-cost hardware. It automatically updates as new data is received from a backend server via Socket.IO, providing a live view of the monitored environment.

## Features

*   **Real-time Data Updates:** Utilizes Socket.IO for seamless, live updates of all dashboard indicators.
*   **People Counter:**
    *   Displays "IN" and "OUT" counts in real-time.
    *   Visualized with a bar chart for current counts and a line chart for flow over time.
*   **Storage Usage Monitoring:**
    *   Progress bar visualization for storage utilization percentage.
    *   Detailed display of used, free, and total storage in GB.
*   **Temperature Display:**
    *   Clear device's temperature reading in Celsius (°C).
    *   Progress bar to visually represent temperature range.
*   **Location Tracking & Mapping:**
    *   Real-time location marker on a Leaflet map.
    *   Display of latitude and longitude coordinates.
    *   Path tracking of location changes over time on the map.
*   **Speedometer Visualization:**
    *   Dynamic speedometer gauge reflecting real-time speed data.
    *   Needle and digital display for speed in km/h.
*   **Interactive Charts:**
    *   **People Flow Over Time Chart:** Line chart showing "IN" and "OUT" counts over a time series, scrollable to view historical data.
    *   **Current People Count Chart:** Bar chart displaying the immediate "IN" and "OUT" counts.
*   **Responsive Design:** Adapts to different screen sizes for optimal viewing on desktops, tablets, and mobile devices.
*   **Visually Appealing Interface:** Modern, dark-themed design with clear data presentation.

## Roadmap - Future Features

The SmartSight Dashboard is continuously being improved. Planned future enhancements include:

*   **Weather Integration:**
    *   Displaying current weather conditions (temperature, humidity, conditions, etc.) relevant to the monitored location.
    *   Potentially integrating weather data into visualizations.
*   **Enhanced 3D Visualizations:**
    *   Exploring opportunities to incorporate 3D elements for more engaging and informative data representation. *(Specific 3D features to be defined)*
*   **Data Logging and History:**
    *   Implementing data persistence to allow for historical data review and analysis beyond the real-time view.
*   **User Authentication and Customization:**
    *   Adding user accounts and roles for access control.
    *   Allowing users to customize the dashboard layout and displayed metrics.
*   **Alerting System:**
    *   Setting up alerts for critical metric thresholds (e.g., high temperature, low storage space, unusual people flow).

## Technologies Used

*   **Frontend:**
    *   HTML5
    *   CSS3
    *   JavaScript (ES6+)
    *   [Chart.js](https://www.chartjs.org/) - for interactive charts
    *   [Leaflet](https://leafletjs.com/) - for interactive maps
    *   [Socket.IO Client](https://socket.io/docs/v4/client-api/) - for real-time communication

## Usage

Once the dashboard is set up and connected to a data-streaming backend, it will automatically display and update in real-time as data is received.

*   **Real-time Indicators:** The cards at the top display current values for People Counter, Storage Usage, Temperature, and Location.
*   **Speedometer & Map:** These sections visualize speed and location data dynamically.
*   **Charts:** The charts at the bottom provide visual representations of People Flow Over Time and Current People Count. The "People Flow Over Time" chart is horizontally scrollable to view more historical data.
