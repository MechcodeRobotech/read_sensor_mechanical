import serial
import csv
import time
from datetime import datetime
import threading
import os

# --- ตั้งค่า Serial ---
SERIAL_PORT = 'COM5' 
BAUD_RATE = 115200

# --- ตั้งค่าไฟล์และความถี่ในการบันทึก (วินาที) ---
FILE_TEMP_PRESS = 'temp_pressure_log.csv'
INTERVAL_TEMP_PRESS = 1.0  # บันทึกทุกๆ 1 วินาที (เปลี่ยนตัวเลขนี้ได้ตามต้องการ)

FILE_PIEZO_MIC = 'piezo_mic_log.csv'
INTERVAL_PIEZO_MIC = 0.1   # บันทึกทุกๆ 0.1 วินาที (10Hz)

# ตัวแปรส่วนกลางสำหรับเก็บข้อมูลล่าสุด
latest_data = {
    'piezo': None,
    'pressure': None,
    'mic': None,
    'temp': None
}

# ใช้ Lock เพื่อป้องกันไม่ให้ Thread แย่งกันอ่าน/เขียนตัวแปรในเวลาเดียวกัน
data_lock = threading.Lock()
is_running = True

def read_serial_data():
    """Thread สำหรับอ่านข้อมูลจาก Serial ตลอดเวลา"""
    global is_running
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"Connected to {SERIAL_PORT}")
        time.sleep(2) 
        ser.reset_input_buffer()
        print("Buffer cleared, start receiving data...\n")

        while is_running:
            if ser.in_waiting > 0:
                raw_data = ser.readline()
                line = raw_data.decode('utf-8', errors='ignore').strip()
                
                if not line:
                    continue
                
                #Print Serial ที่รับมา 
                print(f"Serial Received: {line}")

                data = line.split(',')
                if len(data) == 4:
                    # อัปเดตข้อมูลล่าสุดลงใน Dictionary อย่างปลอดภัย
                    with data_lock:
                        latest_data['piezo'] = data[0]
                        latest_data['pressure'] = data[1]
                        latest_data['mic'] = data[2]
                        latest_data['temp'] = data[3]
                        
    except serial.SerialException:
        print(f"\nError: Could not open port {SERIAL_PORT}. Check connection.")
        is_running = False
    except Exception as e:
        print(f"\nUnexpected Error in Serial Thread: {e}")
        is_running = False
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Serial closed.")

def log_temp_pressure():
    """Thread สำหรับบันทึก Temp และ Pressure"""
    file_exists = os.path.isfile(FILE_TEMP_PRESS)
    
    with open(FILE_TEMP_PRESS, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Timestamp", "Temp(C)", "Pressure(Bar)"])
            
        while is_running:
            with data_lock:
                temp = latest_data['temp']
                pressure = latest_data['pressure']
            
            # ถ้ามีข้อมูลเข้ามาแล้วถึงจะบันทึก
            if temp is not None and pressure is not None:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                writer.writerow([timestamp, temp, pressure])
                file.flush() # บังคับเขียนลงดิสก์ทันที ป้องกันข้อมูลหายถ้าโปรแกรมดับ
                
            time.sleep(INTERVAL_TEMP_PRESS) # รอจนกว่าจะถึงรอบถัดไป

def log_piezo_mic():
    """Thread สำหรับบันทึก Piezo และ Mic"""
    file_exists = os.path.isfile(FILE_PIEZO_MIC)
    
    with open(FILE_PIEZO_MIC, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Timestamp", "Piezo(x100)", "Mic(V)"])
            
        while is_running:
            with data_lock:
                piezo = latest_data['piezo']
                mic = latest_data['mic']
            
            if piezo is not None and mic is not None:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                writer.writerow([timestamp, piezo, mic])
                file.flush()
                
            time.sleep(INTERVAL_PIEZO_MIC)

if __name__ == "__main__":
    print("Initializing Multi-threaded Logger... (Press Ctrl+C to stop)")
    
    # สร้าง Threads
    t_serial = threading.Thread(target=read_serial_data)
    t_tp = threading.Thread(target=log_temp_pressure)
    t_pm = threading.Thread(target=log_piezo_mic)
    
    # เริ่มให้ Thread อ่าน Serial ทำงานก่อน
    t_serial.start()
    
    # รอให้ Hardware รีเซ็ตและมีข้อมูลชุดแรกเข้ามาสักครู่ ค่อยเริ่มบันทึก
    time.sleep(3) 
    
    if is_running:
        t_tp.start()
        t_pm.start()
        print(f"Logging Temp/Pressure every {INTERVAL_TEMP_PRESS}s")
        print(f"Logging Piezo/Mic every {INTERVAL_PIEZO_MIC}s")

    try:
        # Loop หลักมีหน้าที่แค่เลี้ยงโปรแกรมไว้ และรอรับคำสั่ง Ctrl+C
        while is_running:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nCtrl+C detected. Stopping all threads gracefully...")
        is_running = False # ส่งสัญญาณให้ทุก Thread หยุดการทำงานของ loop
        
    # รอให้ทุก Thread ปิดการทำงานตัวเองให้เรียบร้อยก่อนจบโปรแกรม
    t_serial.join()
    t_tp.join()
    t_pm.join()
    print("Program exited successfully.")
