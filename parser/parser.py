import struct
import math


MAGIC_WORD = b'\x02\x01\x04\x03\x06\x05\x08\x07'

HEADER_LENGTH = 40

# TLV types used by the TI example
MMWDEMO_OUTPUT_MSG_TRACKERPROC_3D_TARGET_LIST = 1010
MMWDEMO_OUTPUT_MSG_COMPRESSED_POINTS = 1020
MMWDEMO_OUTPUT_MSG_PRESCENCE_INDICATION = 1021
MMWDEMO_OUTPUT_MSG_TRACKERPROC_TARGET_INDEX  = 1011
MMWDEMO_OUTPUT_MSG_TRACKERPROC_TARGET_HEIGHT = 1012
TARGET_HEIGHT_SIZE = 12  # uint32 + float + float
TLV_TYPE_SIDE_INFO = 7
TRACK_SIZE = 112


class FrameParser:

    def __init__(self):
        self.buffer = bytearray()

    # ---------------------------------------------------------
    # UART input
    # ---------------------------------------------------------

    def append(self, data: bytes):
        """
        Add received UART data to the internal buffer.
        """
        self.buffer.extend(data)

    # ---------------------------------------------------------
    # Frame parser
    # ---------------------------------------------------------

    def get_frame(self):
        """
        Try to extract and decode one complete radar frame.

        Returns:
            dict: Decoded radar frame
            None: If no complete frame is available
        """

        # -----------------------------------------------------
        # 1. Search for Magic Word
        # -----------------------------------------------------

        magic_index = self.buffer.find(MAGIC_WORD)

        if magic_index == -1:

            # Keep the last bytes because the Magic Word can
            # be split between two UART reads.
            keep = len(MAGIC_WORD) - 1

            if len(self.buffer) > keep:
                del self.buffer[:-keep]

            return None

        # Remove garbage before Magic Word
        if magic_index > 0:
            del self.buffer[:magic_index]

        # -----------------------------------------------------
        # 2. Wait for complete header
        # -----------------------------------------------------

        if len(self.buffer) < HEADER_LENGTH:
            return None

        # -----------------------------------------------------
        # 3. Parse header
        # -----------------------------------------------------

        header = struct.unpack(
            '<Q8I',
            self.buffer[:HEADER_LENGTH]
        )

        magic_word = header[0]
        version = header[1]
        packet_length = header[2]
        platform = header[3]
        frame_number = header[4]
        cpu_cycles = header[5]
        num_detected_objects = header[6]
        num_tlvs = header[7]
        subframe_number = header[8]

        # -----------------------------------------------------
        # 4. Validate header
        # -----------------------------------------------------

        if packet_length < HEADER_LENGTH:

            # Invalid packet length.
            # Remove one byte and search for the next
            # possible Magic Word.
            del self.buffer[0]

            return None

        # -----------------------------------------------------
        # 5. Wait for complete frame
        # -----------------------------------------------------

        if len(self.buffer) < packet_length:
            return None

        # -----------------------------------------------------
        # 6. Extract complete frame
        # -----------------------------------------------------

        frame = bytes(self.buffer[:packet_length])

        del self.buffer[:packet_length]

        # ---------------------------------------------------------
        # 7. Parse TLVs
        # ---------------------------------------------------------
        
        objects = []
        tracks = []
        target_indices = []
        target_heights = []
        presence = None

        offset = HEADER_LENGTH

        for tlv_index in range(num_tlvs):

            # ----------------------------------------
            # TLV-Header lesen (8 Bytes)
            # ----------------------------------------
        
            if offset + 8 > len(frame):
                print("ERROR: Not enough data for TLV header")
                break
        
            tlv_type, tlv_length = struct.unpack(
                '<2I',
                frame[offset:offset + 8]
            )
        
            tlv_data_start = offset + 8
            tlv_end        = offset + 8 + tlv_length
            
            # print(f"\nTLV {tlv_index}:")
            # print(f"  Offset: {offset}")
            # print(f"  Type:   {tlv_type}")
            # print(f"  Length: {tlv_length}")
        
            # ----------------------------------------
            # Prüfen ob TLV vollständig im Frame liegt
            # ----------------------------------------
        
            if tlv_end > len(frame):
                print("  ERROR: TLV exceeds frame")
                break
        
            tlv_data = frame[tlv_data_start:tlv_end]
        
            # print(f"  Data length: {len(tlv_data)}")
            # print(f"  Data HEX: {tlv_data.hex(' ')}")
        
            # ----------------------------------------
            # TLV verarbeiten
            # ----------------------------------------

            if tlv_type == MMWDEMO_OUTPUT_MSG_COMPRESSED_POINTS:
                print("  -> Detected Points TLV")
                self._parse_compressed_points(tlv_data, objects)

            elif tlv_type == MMWDEMO_OUTPUT_MSG_TRACKERPROC_3D_TARGET_LIST:
                print("  -> 3D Target List")
                tracks = self._threeD_target_list(tlv_data)

            elif tlv_type == MMWDEMO_OUTPUT_MSG_TRACKERPROC_TARGET_INDEX:
                print("  -> Target Index TLV")
                target_indices = self._parse_target_index(tlv_data)

            elif tlv_type == MMWDEMO_OUTPUT_MSG_TRACKERPROC_TARGET_HEIGHT:
                print("  -> Target Height TLV")
                target_heights = self._parse_target_height(tlv_data)

            elif tlv_type == MMWDEMO_OUTPUT_MSG_PRESCENCE_INDICATION:
                print("  -> Presence Indication TLV")
                presence = self._parse_presence_indication(tlv_data)

            elif tlv_type == TLV_TYPE_SIDE_INFO:
                print("  -> Side Info TLV")
                self._parse_side_info(tlv_data, objects)

            else:
                print("  -> Unknown TLV")

            # Wichtig: zum Beginn des nächsten TLV springen.
            offset = tlv_end

        # -----------------------------------------------------
        # 8. Return decoded frame
        # -----------------------------------------------------

        return {
            "raw": frame,
        
            "magic_word":           magic_word,
            "version":              version,
            "packet_length":        packet_length,
            "platform":             platform,
            "frame_number":         frame_number,
            "cpu_cycles":           cpu_cycles,
            "num_detected_objects": num_detected_objects,
            "num_tlvs":             num_tlvs,
            "subframe_number":      subframe_number,
        
            "objects":              objects,
            "presence":             presence,
            "tracks":               tracks,
            "target_indices":       target_indices,
            "target_heights":       target_heights
        }

    # =========================================================
    # TLV Type 1
    # =========================================================

    def _parse_compressed_points(self, data, objects):
        """
        Parse TLV type 1020.
    
        Format:
    
            5 x float32:
                elevationUnit
                azimuthUnit
                dopplerUnit
                rangeUnit
                snrUnit
    
            Then N points, each 8 bytes:
    
                int8   elevation
                int8   azimuth
                int16  doppler
                uint16 range
                uint16 snr
        """
    
        # -----------------------------------------------------
        # Point units
        # -----------------------------------------------------
    
        if len(data) < 20:
            return
    
        (
            elevation_unit,
            azimuth_unit,
            doppler_unit,
            range_unit,
            snr_unit
        ) = struct.unpack(
            '<5f',
            data[:20]
        )
    
        # -----------------------------------------------------
        # Point data
        # -----------------------------------------------------
    
        point_data = data[20:]
    
        point_size = 8
    
        if len(point_data) % point_size != 0:
            print(
                f"WARNING: Invalid compressed point data length: "
                f"{len(point_data)}"
            )
    
        object_count = len(point_data) // point_size
    
        for i in range(object_count):
    
            offset = i * point_size
    
            elevation_raw, azimuth_raw, doppler_raw, range_raw, snr_raw = struct.unpack(
                '<bbhHH',
                point_data[offset:offset + 8]
            )
    
            # -------------------------------------------------
            # Decompress
            # -------------------------------------------------
    
            elevation = elevation_raw * elevation_unit
            azimuth = azimuth_raw * azimuth_unit
            velocity = doppler_raw * doppler_unit
            radar_range = range_raw * range_unit
            snr = snr_raw * snr_unit
    
            # -------------------------------------------------
            # Spherical -> Cartesian
            #
            # TI coordinate convention:
            #
            # x = range * cos(elevation) * sin(azimuth)
            # y = range * cos(elevation) * cos(azimuth)
            # z = range * sin(elevation)
            # -------------------------------------------------
    
            x = (
                radar_range *
                math.cos(elevation) *
                math.sin(azimuth)
            )
    
            y = (
                radar_range *
                math.cos(elevation) *
                math.cos(azimuth)
            )
    
            z = (
                radar_range *
                math.sin(elevation)
            )
    
            objects.append({
                "x": x,
                "y": y,
                "z": z,
    
                "v": velocity,
    
                "range": radar_range,
                "azimuth": math.degrees(azimuth),
                "elevation": math.degrees(elevation),
    
                "snr": snr,
                "noise": None
            })
            
    def _threeD_target_list(self, payload):
        """
        Parse TLV type 1010.
    
        Format:
    
            tid - Track ID                                                  uint32_t     4
            posX - Target Position (meters) in X dimension                  float     4
            posY - Target Position (meters) in Y dimension                  float     4
            posZ - Target Position (meters) in Z dimension                  float     4
            velX - Target Velocity (meters/second) in X dimension           float     4
            velY - Target Velocity (meters/second) in Y dimension           float     4
            velZ - Target Velocity (meters/second) in Z dimension           float     4
            accX - Target Acceleration (meters/second^2) in X dimension     float     4
            accY - Target Acceleration (meters/second^2) in Y dimension     float     4
            accZ - Target Acceleration (meters/second^2) in Z dimension     float     4
            ec[16] - Tracking error covariance matrix                       float     64
            g - Gating function gain                                        float     4
            confidenceLevel                                                 float     4
            
            Total size per object: 112 bytes.
        """
    
        # -----------------------------------------------------
        # Point units
        # -----------------------------------------------------
    
        if len(payload) % TRACK_SIZE != 0:
            print(
                f"WARNING: TLV 1010 payload has invalid length: "
                f"{len(payload)} bytes "
                f"(not divisible by {TRACK_SIZE})"
            )
    
        tracks = []
    
        number_of_tracks = len(payload) // TRACK_SIZE
    
        for i in range(number_of_tracks):
    
            offset = i * TRACK_SIZE
    
            # uint32 + 9 floats + 16 floats + 2 floats
            values = struct.unpack_from(
                "<I 9f 16f 2f",
                payload,
                offset
            )
    
            tid = values[0]
    
            posX = values[1]
            posY = values[2]
            posZ = values[3]
    
            velX = values[4]
            velY = values[5]
            velZ = values[6]
    
            accX = values[7]
            accY = values[8]
            accZ = values[9]
    
            ec = values[10:26]
    
            g = values[26]
            confidenceLevel = values[27]
    
            track = {
                "tid": tid,
    
                "posX": posX,
                "posY": posY,
                "posZ": posZ,
    
                "velX": velX,
                "velY": velY,
                "velZ": velZ,
    
                "accX": accX,
                "accY": accY,
                "accZ": accZ,
    
                "ec": ec,
    
                "g": g,
                "confidenceLevel": confidenceLevel
            }
    
            tracks.append(track)
    
            # print(f"\nTrack {tid}")
            # print(
            #     f"  Position:     "
            #     f"X={posX:.3f} m, "
            #     f"Y={posY:.3f} m, "
            #     f"Z={posZ:.3f} m"
            # )
            #
            # print(
            #     f"  Velocity:     "
            #     f"X={velX:.3f} m/s, "
            #     f"Y={velY:.3f} m/s, "
            #     f"Z={velZ:.3f} m/s"
            # )
            #
            # print(
            #     f"  Acceleration: "
            #     f"X={accX:.3f} m/s2, "
            #     f"Y={accY:.3f} m/s2, "
            #     f"Z={accZ:.3f} m/s2"
            # )
            #
            # print(f"  Gating gain:  {g:.3f}")
            # print(f"  Confidence:   {confidenceLevel:.3f}")
    
        return tracks
    
    # =========================================================
    # TLV Type 1021
    # =========================================================
    
    def _parse_presence_indication(self, data):
        """
        Parse TLV type 1021 (MMWDEMO_OUTPUT_MSG_PRESCENCE_INDICATION).
    
        Format:
            uint32  presenceIndication  4 Bytes
    
            0 = No presence detected
            1 = Presence detected
        """
    
        if len(data) < 4:
            print("WARNING: Presence Indication TLV too short")
            return None
    
        (presence,) = struct.unpack('<I', data[:4])
    
        print(f"  Presence detected: {'YES' if presence else 'NO'} ({presence})")
    
        return presence

    # =========================================================
    # TLV Type 7
    # =========================================================

    def _parse_side_info(self, data, objects):
        """
        Parse TLV type 7.

        Each object contains:

            SNR   : uint16
            Noise : uint16

        4 bytes per object.
        """

        object_count = len(data) // 4

        for i in range(object_count):

            offset = i * 4

            snr, noise = struct.unpack(
                '<2H',
                data[offset:offset + 4]
            )

            # Make sure the object exists.
            if i < len(objects):

                objects[i]["snr"] = snr
                objects[i]["noise"] = noise
                
                
    # =========================================================
    # TLV Type 1011
    # =========================================================
    
    def _parse_target_index(self, data):
        """
        Parse TLV type 1011 (MMWDEMO_OUTPUT_MSG_TRACKERPROC_TARGET_INDEX).
    
        Format:
            N x uint8  (one byte per point)
    
            Value 253 = point not associated to any target (noise)
            Value 254 = point associated to a target but outside gating area
            Value 0-N = target ID the point is associated to
        """
    
        if len(data) == 0:
            print("WARNING: Target Index TLV is empty")
            return []
    
        indices = list(struct.unpack(f'<{len(data)}B', data))
    
        # for i, idx in enumerate(indices):
        #     if idx == 255:
        #         label = "not associated with a target"
        #     elif idx == 254:
        #         label = "outside gating"
        #     elif idx == 253:
        #         label = "noise"
        #     else:
        #         label = f"Target {idx}"
        #
        #     print(f"  Point {i:3d} -> {label}")
    
        return indices
    
    
    # =========================================================
    # TLV Type 1012
    # =========================================================
    
    def _parse_target_height(self, data):
        """
        Parse TLV type 1012 (MMWDEMO_OUTPUT_MSG_TRACKERPROC_TARGET_HEIGHT).
    
        Format per entry (12 Bytes):
    
            targetID  uint32_t  4
            maxZ      float     4
            minZ      float     4
        """
    
        if len(data) % TARGET_HEIGHT_SIZE != 0:
            print(
                f"WARNING: Target Height TLV has invalid length: "
                f"{len(data)} bytes "
                f"(not divisible by {TARGET_HEIGHT_SIZE})"
            )
    
        heights = []
    
        num_entries = len(data) // TARGET_HEIGHT_SIZE
    
        for i in range(num_entries):
    
            offset = i * TARGET_HEIGHT_SIZE
    
            target_id, max_z, min_z = struct.unpack_from(
                '<Iff',
                data,
                offset
            )
    
            height = max_z - min_z
    
            entry = {
                "target_id": target_id,
                "max_z":     max_z,
                "min_z":     min_z,
                "height":    height
            }
    
            heights.append(entry)
    
            print(
                f"  Target {target_id}: "
                f"minZ={min_z:.3f} m, "
                f"maxZ={max_z:.3f} m, "
                f"height={height:.3f} m"
            )
    
        return heights