#!/usr/bin/env python3
"""
IoT Dashboard Data Simulator
Simulates realistic sensor data for the dashboard including:
- People counter (IN/OUT)
- Storage usage
- Temperature
- GPS location with movement
- Vehicle speed
"""

import json
import time
import random
import math
import threading
from datetime import datetime
import paho.mqtt.client as mqtt

class IoTDataSimulator:
    def __init__(self, mqtt_broker="192.168.12.3", mqtt_port=1883):
        # MQTT Configuration
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.mqtt_topic = "dashboard/data"
        self.client = mqtt.Client()
        
        # Simulation parameters
        self.running = False
        
        # People counter state
        self.people_in = 0
        self.people_out = 0
        self.max_occupancy = 50
        
        # Storage simulation (starts with some usage)
        self.total_storage_gb = 1000.0
        self.used_storage_gb = 350.0
        
        # Temperature simulation (room temperature with HVAC cycles)
        self.base_temp = 24.0  # Base room temperature
        self.temp_variation = 0
        
        # Location simulation (starts at default location from HTML)
        self.latitude = 10.731976073258629
        self.longitude = 106.69932603584631
        self.location_step = 0.0001  # Movement step size
        self.movement_angle = 0
        
        # Speed simulation
        self.current_speed = 0.0
        self.target_speed = 0.0
        self.speed_change_counter = 0
        
        # Setup MQTT callbacks
        self.setup_mqtt()
    
    def setup_mqtt(self):
        """Setup MQTT client with callbacks"""
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print(f"✅ Connected to MQTT broker at {self.mqtt_broker}:{self.mqtt_port}")
            else:
                print(f"❌ Failed to connect to MQTT broker. Code: {rc}")
        
        def on_disconnect(client, userdata, rc):
            print(f"📡 Disconnected from MQTT broker. Code: {rc}")
        
        def on_publish(client, userdata, mid):
            print(f"📤 Data published (Message ID: {mid})")
        
        self.client.on_connect = on_connect
        self.client.on_disconnect = on_disconnect
        self.client.on_publish = on_publish
    
    def connect_mqtt(self):
        """Connect to MQTT broker"""
        try:
            print(f"🔗 Connecting to MQTT broker {self.mqtt_broker}:{self.mqtt_port}...")
            self.client.connect(self.mqtt_broker, self.mqtt_port, 60)
            self.client.loop_start()
            return True
        except Exception as e:
            print(f"❌ MQTT connection failed: {e}")
            return False
    
    def simulate_people_counter(self):
        """Simulate realistic people counting with building occupancy patterns"""
        current_hour = datetime.now().hour
        
        # Higher activity during business hours (8-18)
        if 8 <= current_hour <= 18:
            in_probability = 0.3
            out_probability = 0.25
        else:
            in_probability = 0.1
            out_probability = 0.15
        
        # Simulate people entering
        if random.random() < in_probability:
            if self.people_in - self.people_out < self.max_occupancy:
                self.people_in += random.randint(1, 3)
        
        # Simulate people leaving
        if random.random() < out_probability:
            if self.people_in > self.people_out:
                self.people_out += random.randint(1, 2)
    
    def simulate_storage(self):
        """Simulate storage usage with gradual changes"""
        # Simulate file operations (writing/deleting)
        change = random.uniform(-2.0, 5.0)  # More likely to increase
        self.used_storage_gb += change
        
        # Keep within realistic bounds
        self.used_storage_gb = max(50.0, min(950.0, self.used_storage_gb))
    
    def simulate_temperature(self):
        """Simulate temperature with HVAC cycles and external factors"""
        current_hour = datetime.now().hour
        
        # Daily temperature cycle (warmer during day)
        daily_cycle = 2 * math.sin((current_hour - 6) * math.pi / 12)
        
        # HVAC cycling
        self.temp_variation += random.uniform(-0.5, 0.5)
        self.temp_variation = max(-3, min(3, self.temp_variation))
        
        # Random fluctuations
        noise = random.uniform(-0.2, 0.2)
        
        return self.base_temp + daily_cycle + self.temp_variation + noise
    
    def simulate_location(self):
        """Simulate GPS movement in a realistic pattern"""
        # Simulate movement along roads/paths
        self.movement_angle += random.uniform(-30, 30)  # Change direction slightly
        
        # Convert angle to radians
        angle_rad = math.radians(self.movement_angle)
        
        # Move in the current direction
        lat_change = self.location_step * math.cos(angle_rad)
        lon_change = self.location_step * math.sin(angle_rad)
        
        self.latitude += lat_change
        self.longitude += lon_change
        
        # Keep within a reasonable area (about 1km radius)
        center_lat, center_lon = 10.731976073258629, 106.69932603584631
        max_distance = 0.01  # Roughly 1km
        
        lat_diff = self.latitude - center_lat
        lon_diff = self.longitude - center_lon
        distance = math.sqrt(lat_diff**2 + lon_diff**2)
        
        if distance > max_distance:
            # Return towards center
            self.latitude = center_lat + (lat_diff / distance) * max_distance * 0.9
            self.longitude = center_lon + (lon_diff / distance) * max_distance * 0.9
            self.movement_angle += 180  # Turn around
    
    def simulate_speed(self):
        """Simulate vehicle speed with realistic acceleration/deceleration"""
        self.speed_change_counter += 1
        
        # Change target speed occasionally
        if self.speed_change_counter % 10 == 0:
            speed_scenarios = [0, 15, 30, 50, 80, 120, 60, 40]  # km/h
            self.target_speed = random.choice(speed_scenarios)
        
        # Gradually move towards target speed
        speed_diff = self.target_speed - self.current_speed
        if abs(speed_diff) > 1:
            acceleration = 2.0 if speed_diff > 0 else -3.0  # Deceleration is faster
            self.current_speed += acceleration + random.uniform(-1, 1)
        else:
            self.current_speed = self.target_speed + random.uniform(-2, 2)
        
        # Keep speed realistic
        self.current_speed = max(0, min(180, self.current_speed))
        return self.current_speed
    
    def generate_data(self):
        """Generate complete sensor data package"""
        self.simulate_people_counter()
        self.simulate_storage()
        self.simulate_location()
        
        temperature = self.simulate_temperature()
        speed = self.simulate_speed()
        
        # Calculate storage percentages
        free_gb = self.total_storage_gb - self.used_storage_gb
        usage_percent = (self.used_storage_gb / self.total_storage_gb) * 100
        
        data = {
            "timestamp": datetime.now().isoformat(),
            "down_up_count": self.people_in,      # People IN
            "up_down_count": self.people_out,     # People OUT
            "usage_percent": round(usage_percent, 2),
            "used_gb": round(self.used_storage_gb, 2),
            "free_gb": round(free_gb, 2),
            "total_gb": self.total_storage_gb,
            "temperature": round(temperature, 1),
            "latitude": round(self.latitude, 8),
            "longitude": round(self.longitude, 8),
            "speed": round(speed, 1)
        }
        
        return data
    
    def publish_data(self, data):
        """Publish data to MQTT topic"""
        try:
            json_data = json.dumps(data)
            result = self.client.publish(self.mqtt_topic, json_data)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                print(f"📡 Published: People IN:{data['down_up_count']} OUT:{data['up_down_count']}, "
                      f"Temp:{data['temperature']}°C, Speed:{data['speed']}km/h, "
                      f"Storage:{data['usage_percent']:.1f}%")
            else:
                print(f"❌ Failed to publish data. Result code: {result.rc}")
                
        except Exception as e:
            print(f"❌ Error publishing data: {e}")
    
    def run_simulation(self, interval=2):
        """Run the main simulation loop"""
        if not self.connect_mqtt():
            return
        
        self.running = True
        print(f"🚀 Starting IoT simulation (interval: {interval}s)")
        print("📊 Dashboard data simulation running...")
        print("🔄 Press Ctrl+C to stop")
        
        try:
            while self.running:
                data = self.generate_data()
                self.publish_data(data)
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n🛑 Simulation stopped by user")
        except Exception as e:
            print(f"❌ Simulation error: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the simulation and cleanup"""
        self.running = False
        self.client.loop_stop()
        self.client.disconnect()
        print("🔌 Disconnected from MQTT broker")
        print("✅ Simulation stopped")

def main():
    print("🌐 IoT Dashboard Data Simulator")
    print("=" * 40)
    
    # Configuration
    mqtt_broker = input("Enter MQTT broker IP (default: 192.168.12.3): ").strip()
    if not mqtt_broker:
        mqtt_broker = "192.168.100.1"
    
    mqtt_port = input("Enter MQTT port (default: 1883): ").strip()
    if not mqtt_port:
        mqtt_port = 1883
    else:
        mqtt_port = int(mqtt_port)
    
    interval = input("Enter update interval in seconds (default: 2): ").strip()
    if not interval:
        interval = 2
    else:
        interval = float(interval)
    
    print(f"\n📡 MQTT Broker: {mqtt_broker}:{mqtt_port}")
    print(f"⏱️  Update Interval: {interval}s")
    print(f"📂 Topic: dashboard/data")
    
    # Create and run simulator
    simulator = IoTDataSimulator(mqtt_broker, mqtt_port)
    simulator.run_simulation(interval)

if __name__ == "__main__":
    main()
