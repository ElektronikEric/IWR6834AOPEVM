from uart import UARTReader
from parser.parser import FrameParser
from radar_cli.cli import RadarCLI
from visualizer.visualizer import RadarVisualizer
import time

DEBUG_OBJECTS = False
visualizer = RadarVisualizer()

uart = UARTReader("COM31")
parser = FrameParser()

# FPS-Messung einmalig initialisieren
processed_frames = 0
last_fps_time = time.perf_counter()

with open("AOP_6m_default.cfg", "r", encoding="utf-8") as f:
    config = f.read()

radar = RadarCLI("COM33")

try:
    radar.send_config(config)
finally:
    radar.close()

print("Waiting for radar frames...")

try:

    while True:

        data = uart.read(1024)

        if len(data) == 0:
            continue

        parser.append(data)

        while True:

            frame = parser.get_frame()

            if frame is None:
                break

            visualizer.update(frame)
            
            # TLV 1010: Ein Track entspricht einer verfolgten Person.
            # Optionaler Confidence-Filter verhindert instabile Tracks.
            MIN_TRACK_CONFIDENCE = 0.5
            
            persons = [
                track
                for track in frame.get("tracks", [])
                if track.get("confidenceLevel", 0.0) >= MIN_TRACK_CONFIDENCE
            ]
            
            person_count = len(persons)
            
            print(
                f"\rPersons: {person_count} | "
                f"Tracks: {len(frame.get('tracks', []))} | "
                f"Objects: {len(frame.get('objects', []))} | "
                f"Presence: {frame.get('presence')}",
                end="",
                flush=True
            )
            
            # FPS nach der Verarbeitung eines Frames erhöhen
            processed_frames += 1

            now = time.perf_counter()

            if now - last_fps_time >= 1.0:
                print(
                    f"\rParser/Visualizer rate: {processed_frames} frames/s",
                    end="",
                    flush=True
                )

                processed_frames = 0
                last_fps_time = now
                
            if DEBUG_OBJECTS:
                print()
                print("========================================")
                print("Frame received")
                print("========================================")
    
                print("Frame number:        ", frame["frame_number"])
                print("Packet length:       ", frame["packet_length"])
                print("Detected objects:    ", frame["num_detected_objects"])
                print("Number of TLVs:      ", frame["num_tlvs"])
                print("Presence:            ", frame["presence"])
    
                # -------------------------------------------------
                # Detected objects
                # -------------------------------------------------
    
                print()
                print("=" * 40)
                print(f"Frame number: {frame['frame_number']}")
                print(f"Detected objects: {frame['num_detected_objects']}")
                print(f"Parsed objects: {len(frame['objects'])}")

            for i, obj in enumerate(frame["objects"]):
                if DEBUG_OBJECTS:
                    print(f"\nObject {i + 1}")
                    print(f"  X:         {obj['x']:.3f} m")
                    print(f"  Y:         {obj['y']:.3f} m")
                    print(f"  Z:         {obj['z']:.3f} m")
                    print(f"  Velocity:  {obj['v']:.3f} m/s")
                    print(f"  Range:     {obj['range']:.3f} m")
                    print(f"  Azimuth:   {obj['azimuth']:.2f} deg")
                    print(f"  Elevation: {obj['elevation']:.2f} deg")
                    print(f"  SNR:       {obj['snr']}")
                    print(f"  Noise:     {obj['noise']}")

                # Target Index für diesen Punkt
                if DEBUG_OBJECTS:
                    if i < len(frame["target_indices"]):
                        idx = frame["target_indices"][i]
                        if idx == 253:
                            label = "noise"
                        elif idx == 254:
                            label = "outside gating"
                        else:
                            label = f"Target {idx}"
                        print(f"  Target:    {label}")

            # -------------------------------------------------
            # Tracks (TLV 1010)
            # -------------------------------------------------
            if DEBUG_OBJECTS:
                if frame["tracks"]:
                    print()
                    print("=" * 40)
                    print(f"Tracks: {len(frame['tracks'])}")
    
                    for track in frame["tracks"]:
                        print(f"\nTrack {track['tid']}")
                        print(
                            f"  Position:     "
                            f"X={track['posX']:.3f} m, "
                            f"Y={track['posY']:.3f} m, "
                            f"Z={track['posZ']:.3f} m"
                        )
                        print(
                            f"  Velocity:     "
                            f"X={track['velX']:.3f} m/s, "
                            f"Y={track['velY']:.3f} m/s, "
                            f"Z={track['velZ']:.3f} m/s"
                        )
                        print(f"  Confidence:   {track['confidenceLevel']:.3f}")

            # -------------------------------------------------
            # Target Heights (TLV 1012)
            # -------------------------------------------------
            if DEBUG_OBJECTS:
                if frame["target_heights"]:
                    print()
                    print("=" * 40)
                    print(f"Target Heights: {len(frame['target_heights'])}")
    
                    for entry in frame["target_heights"]:
                        print(
                            f"  Target {entry['target_id']}: "
                            f"minZ={entry['min_z']:.3f} m, "
                            f"maxZ={entry['max_z']:.3f} m, "
                            f"height={entry['height']:.3f} m"
                        )

            # -------------------------------------------------
            # HEX output
            # -------------------------------------------------
            if DEBUG_OBJECTS:
                print()
                print("HEX:")
                print(frame["raw"].hex(" "))

except KeyboardInterrupt:
    print()
    print("Program stopped.")

finally:
    visualizer.close()
    uart.close()