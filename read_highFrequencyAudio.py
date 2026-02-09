import sounddevice as sd
import soundfile as sf
import queue
import numpy as np

# 1. การตั้งค่า
samplerate = 44100
# Input ต้องเป็น 2 (เพราะรับมาจาก Zoom UAC-2 แบบ Stereo)
input_channels = 2  
filename_ch1 = 'output_channel_1.wav'
filename_ch2 = 'output_channel_2.wav'

q = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print(status)
    q.put(indata.copy())

try:
    print("กำลังบันทึกแยก 2 Channels... (กด Ctrl+C เพื่อหยุด)")

    # เปิดไฟล์รอไว้ 2 ไฟล์ (สังเกต channels=1 คือบันทึกแบบ Mono)
    # ใช้ file1 และ file2 เพื่อเขียนแยกกัน
    with sf.SoundFile(filename_ch1, mode='w', samplerate=samplerate, channels=1) as file1, \
         sf.SoundFile(filename_ch2, mode='w', samplerate=samplerate, channels=1) as file2:

        # เปิดรับเสียงจาก UAC-2 (รับมาทีเดียว 2 ช่อง)
        with sd.InputStream(samplerate=samplerate, channels=input_channels, callback=callback):
            while True:
                # ดึงข้อมูลก้อนรวมออกมา
                data = q.get()
                
                # --- หัวใจสำคัญอยู่ตรงนี้ (NumPy Slicing) ---
                # data[:, 0] หมายถึง เอาทุกแถว แต่เอาเฉพาะคอลัมน์ที่ 0 (Channel 1/Left)
                # data[:, 1] หมายถึง เอาทุกแถว แต่เอาเฉพาะคอลัมน์ที่ 1 (Channel 2/Right)
                
                file1.write(data[:, 0]) 
                file2.write(data[:, 1])

except KeyboardInterrupt:
    print("\nหยุดบันทึกแล้ว")
    print(f"Saved: {filename_ch1}")
    print(f"Saved: {filename_ch2}")
except Exception as e:
    print(f"\nError: {e}")