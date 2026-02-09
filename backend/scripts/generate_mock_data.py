#!/usr/bin/env python3
"""
Mock Data Generator for PowerGuard
Generates realistic smart meter data with intentional anomalies for testing.
"""

import csv
import random
import math
from datetime import datetime, timedelta
from typing import List, Tuple
import argparse
import os

# Default configuration
DEFAULT_NUM_METERS = 50
DEFAULT_DAYS = 30
DEFAULT_ANOMALY_RATE = 0.15  # 15% of meters will have anomalies
OUTPUT_FILE = "mock_meter_data.csv"


def generate_normal_pattern(hour: int, base_consumption: float) -> float:
    """
    Generate normal household consumption pattern.
    
    Typical pattern:
    - Low at night (0-5 AM)
    - Morning peak (6-9 AM)
    - Moderate during day (10 AM - 5 PM)
    - Evening peak (6-10 PM)
    - Decline at night (11 PM - midnight)
    """
    # Base hourly pattern multipliers
    hourly_pattern = {
        0: 0.3, 1: 0.2, 2: 0.2, 3: 0.2, 4: 0.2, 5: 0.3,
        6: 0.6, 7: 0.8, 8: 0.9, 9: 0.7,
        10: 0.5, 11: 0.5, 12: 0.6, 13: 0.5, 14: 0.4, 15: 0.4,
        16: 0.5, 17: 0.7, 18: 0.9, 19: 1.0, 20: 0.9, 21: 0.8,
        22: 0.6, 23: 0.4
    }
    
    multiplier = hourly_pattern[hour]
    # Add some random variation (±20%)
    variation = random.uniform(0.8, 1.2)
    
    return base_consumption * multiplier * variation


def generate_anomaly_pattern(
    hour: int, 
    base_consumption: float, 
    anomaly_type: str
) -> float:
    """
    Generate anomalous consumption pattern.
    
    Anomaly types:
    - theft: Unusually low consumption (meter tampering)
    - night_spike: High consumption during night hours
    - constant: Flat consumption regardless of time
    - extreme: Random extreme spikes
    """
    if anomaly_type == "theft":
        # Very low consumption - possible meter bypass
        return base_consumption * random.uniform(0.05, 0.15)
    
    elif anomaly_type == "night_spike":
        # High consumption during night hours
        if 22 <= hour or hour <= 5:
            return base_consumption * random.uniform(1.5, 3.0)
        else:
            return generate_normal_pattern(hour, base_consumption)
    
    elif anomaly_type == "constant":
        # Flat consumption - possible illegal connection
        return base_consumption * random.uniform(0.8, 1.2)
    
    elif anomaly_type == "extreme":
        # Random extreme spikes
        if random.random() < 0.3:  # 30% chance of spike
            return base_consumption * random.uniform(3, 8)
        else:
            return generate_normal_pattern(hour, base_consumption)
    
    else:
        return generate_normal_pattern(hour, base_consumption)


def generate_meter_data(
    meter_id: str,
    start_date: datetime,
    num_days: int,
    is_anomalous: bool,
    anomaly_type: str = None
) -> List[Tuple[str, str, float]]:
    """
    Generate hourly readings for a single meter.
    
    Returns list of tuples: (meter_id, timestamp, consumption_kwh)
    """
    readings = []
    
    # Base consumption varies by meter (1-5 kWh average)
    base_consumption = random.uniform(1.0, 5.0)
    
    # Weekend factor
    weekend_factor = random.uniform(1.1, 1.3)
    
    current_time = start_date
    for day in range(num_days):
        is_weekend = current_time.weekday() >= 5
        day_factor = weekend_factor if is_weekend else 1.0
        
        for hour in range(24):
            timestamp = current_time + timedelta(hours=hour)
            
            if is_anomalous:
                consumption = generate_anomaly_pattern(
                    hour, 
                    base_consumption * day_factor, 
                    anomaly_type
                )
            else:
                consumption = generate_normal_pattern(
                    hour, 
                    base_consumption * day_factor
                )
            
            # Ensure non-negative
            consumption = max(0, consumption)
            
            readings.append((
                meter_id,
                timestamp.strftime("%Y-%m-%dT%H:%M:%S"),
                round(consumption, 3)
            ))
        
        current_time += timedelta(days=1)
    
    return readings


def generate_mock_data(
    num_meters: int = DEFAULT_NUM_METERS,
    num_days: int = DEFAULT_DAYS,
    anomaly_rate: float = DEFAULT_ANOMALY_RATE,
    output_file: str = OUTPUT_FILE
) -> dict:
    """
    Generate complete mock dataset.
    
    Args:
        num_meters: Number of meters to simulate
        num_days: Number of days of data
        anomaly_rate: Proportion of anomalous meters
        output_file: Output CSV file path
        
    Returns:
        Summary statistics
    """
    start_date = datetime.now() - timedelta(days=num_days)
    
    all_readings = []
    anomaly_types = ["theft", "night_spike", "constant", "extreme"]
    
    num_anomalous = int(num_meters * anomaly_rate)
    anomalous_meters = random.sample(range(num_meters), num_anomalous)
    
    meter_info = []
    
    print(f"Generating data for {num_meters} meters over {num_days} days...")
    
    for i in range(num_meters):
        meter_id = f"METER_{i+1:04d}"
        is_anomalous = i in anomalous_meters
        
        if is_anomalous:
            anomaly_type = random.choice(anomaly_types)
            meter_info.append({
                "meter_id": meter_id,
                "is_anomalous": True,
                "anomaly_type": anomaly_type
            })
        else:
            anomaly_type = None
            meter_info.append({
                "meter_id": meter_id,
                "is_anomalous": False,
                "anomaly_type": None
            })
        
        readings = generate_meter_data(
            meter_id,
            start_date,
            num_days,
            is_anomalous,
            anomaly_type
        )
        all_readings.extend(readings)
        
        if (i + 1) % 10 == 0:
            print(f"  Generated {i + 1}/{num_meters} meters...")
    
    # Write to CSV
    print(f"Writing {len(all_readings)} readings to {output_file}...")
    
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['meter_id', 'timestamp', 'consumption_kwh'])
        writer.writerows(all_readings)
    
    # Write meter info for reference
    info_file = output_file.replace('.csv', '_info.csv')
    with open(info_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['meter_id', 'is_anomalous', 'anomaly_type'])
        writer.writeheader()
        writer.writerows(meter_info)
    
    summary = {
        "total_meters": num_meters,
        "total_readings": len(all_readings),
        "anomalous_meters": num_anomalous,
        "days": num_days,
        "output_file": output_file,
        "info_file": info_file,
        "anomaly_breakdown": {}
    }
    
    # Count anomaly types
    for info in meter_info:
        if info["is_anomalous"]:
            atype = info["anomaly_type"]
            summary["anomaly_breakdown"][atype] = summary["anomaly_breakdown"].get(atype, 0) + 1
    
    return summary


def main():
    parser = argparse.ArgumentParser(
        description="Generate mock smart meter data for PowerGuard"
    )
    parser.add_argument(
        "-m", "--meters",
        type=int,
        default=DEFAULT_NUM_METERS,
        help=f"Number of meters (default: {DEFAULT_NUM_METERS})"
    )
    parser.add_argument(
        "-d", "--days",
        type=int,
        default=DEFAULT_DAYS,
        help=f"Number of days (default: {DEFAULT_DAYS})"
    )
    parser.add_argument(
        "-a", "--anomaly-rate",
        type=float,
        default=DEFAULT_ANOMALY_RATE,
        help=f"Anomaly rate 0-1 (default: {DEFAULT_ANOMALY_RATE})"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=OUTPUT_FILE,
        help=f"Output file (default: {OUTPUT_FILE})"
    )
    
    args = parser.parse_args()
    
    summary = generate_mock_data(
        num_meters=args.meters,
        num_days=args.days,
        anomaly_rate=args.anomaly_rate,
        output_file=args.output
    )
    
    print("\n" + "=" * 50)
    print("Mock Data Generation Complete!")
    print("=" * 50)
    print(f"Total meters:      {summary['total_meters']}")
    print(f"Total readings:    {summary['total_readings']:,}")
    print(f"Anomalous meters:  {summary['anomalous_meters']}")
    print(f"Days of data:      {summary['days']}")
    print(f"\nOutput files:")
    print(f"  - {summary['output_file']}")
    print(f"  - {summary['info_file']}")
    print(f"\nAnomaly breakdown:")
    for atype, count in summary['anomaly_breakdown'].items():
        print(f"  - {atype}: {count} meters")


if __name__ == "__main__":
    main()
