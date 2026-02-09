import serial
import csv
import time
from datetime import datetime

# --- ตั้งค่า ---
SERIAL_PORT = 'COM5' 
BAUD_RATE = 115200
FILENAME = 'sensor_log.csv'

try:
    # เชื่อมต่อ Serial
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"Connected to {SERIAL_PORT}")
    
    # *** เพิ่ม: รอให้ Arduino รีเซ็ตเสร็จและล้างขยะใน buffer ***
    time.sleep(2) 
    ser.reset_input_buffer()
    print("Buffer cleared, ready to log.")

    # เปิดไฟล์ CSV เพื่อเขียน
    with open(FILENAME, mode='a', newline='') as file:
        writer = csv.writer(file)
        
        if file.tell() == 0:
            writer.writerow(["Timestamp", "Piezo(x100)", "Pressure(kPa)", "Mic(V)", "Temp(C)"])
            print("Created Header...")

        print("Start Logging... (Press Ctrl+C to stop)")
        
        while True:
            if ser.in_waiting > 0:
                try:
                    # อ่านข้อมูลดิบมาก่อน
                    raw_data = ser.readline()
                    
                    # *** แก้ไข: ใช้ errors='ignore' หรือ 'replace' เพื่อป้องกันโปรแกรมหลุด ***
                    line = raw_data.decode('utf-8', errors='ignore').strip()
                    
                    # ถ้า line ว่าง (เพราะ decode ไม่ออกทั้งหมด) ให้ข้ามไป
                    if not line:
                        continue

                    # แยกข้อมูลด้วยเครื่องหมาย ,
                    data = line.split(',')
                    
                    # ตรวจสอบว่าข้อมูลมาครบ 4 ตัวไหม
                    if len(data) == 4:
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        row = [timestamp] + data
                        
                        writer.writerow(row)
                        print(f"Logged: {row}")
                    else:
                        # กรณีข้อมูลมาไม่ครบ หรือเป็นบรรทัดขยะที่หลุดรอดมา
                        # print(f"Skipped incomplete data: {line}") 
                        pass 

                except UnicodeDecodeError:
                    # กันเหนียว: เผื่อ errors='ignore' เอาไม่อยู่ (แต่ปกติเอาอยู่)
                    print("Decode Error occurred, skipping line.")
                    continue
                except ValueError:
                    print(f"Value Error: {line}")
                    continue

except serial.SerialException:
    print(f"Error: Could not open port {SERIAL_PORT}. Check connection or Close Arduino IDE Serial Monitor.")
except KeyboardInterrupt:
    print("\nLogging Stopped by User.")
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("Serial closed.")