#!/usr/bin/env python3
import sys
import os
from datetime import datetime

try:
    import bencodepy
except ImportError:
    print("需要安装 bencodepy 库")
    print("运行: pip install bencodepy")
    sys.exit(1)


def format_bytes(bytes_value):
    """格式化字节数"""
    if bytes_value < 1024:
        return f"{bytes_value} B"
    elif bytes_value < 1024 * 1024:
        return f"{bytes_value / 1024:.2f} KB"
    elif bytes_value < 1024 * 1024 * 1024:
        return f"{bytes_value / (1024 * 1024):.2f} MB"
    else:
        return f"{bytes_value / (1024 * 1024 * 1024):.2f} GB"


def format_time(seconds):
    """格式化时间"""
    if seconds < 60:
        return f"{seconds} 秒"
    elif seconds < 3600:
        return f"{seconds // 60} 分钟 {seconds % 60} 秒"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours} 小时 {minutes} 分钟"


def format_timestamp(timestamp):
    """格式化时间戳"""
    if timestamp > 0:
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    return "N/A"


def decode_bitfield(bitfield_bytes, num_pieces=None):
    """解码 bitfield"""
    if not bitfield_bytes:
        return []

    bits = []
    for byte in bitfield_bytes:
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)

    if num_pieces:
        bits = bits[:num_pieces]

    return bits


def analyze_pieces(bitfield_bytes, num_pieces=None):
    """分析 pieces 完成情况"""
    bits = decode_bitfield(bitfield_bytes, num_pieces)
    if not bits:
        return 0, 0, 0.0

    completed = sum(bits)
    total = len(bits)
    percentage = (completed / total * 100) if total > 0 else 0

    return completed, total, percentage


def read_fastresume(file_path):
    """读取并解析 fastresume 文件"""

    if not os.path.exists(file_path):
        print(f"错误: 文件不存在: {file_path}")
        return None

    print(f"正在读取文件: {file_path}")
    print(f"文件大小: {format_bytes(os.path.getsize(file_path))}")
    print("=" * 80)

    try:
        with open(file_path, 'rb') as f:
            data = bencodepy.decode(f.read())

        print("\n✓ Bencode 格式验证成功\n")

        print("=" * 80)
        print("基本信息")
        print("=" * 80)

        file_format = data.get(b'file-format', b'').decode('utf-8', errors='ignore')
        file_version = data.get(b'file-version', 0)
        print(f"文件格式: {file_format}")
        print(f"文件版本: {file_version}")

        if file_format != "libtorrent resume file":
            print("⚠️  警告: 文件格式标识不正确")

        info_hash = data.get(b'info-hash', b'')
        if info_hash:
            if len(info_hash) == 20:
                print(f"Info Hash (v1): {info_hash.hex()}")
            else:
                print(f"Info Hash (v1): {info_hash.hex()} (长度异常: {len(info_hash)} 字节)")

        info_hash2 = data.get(b'info-hash2', b'')
        if info_hash2:
            if len(info_hash2) == 32:
                print(f"Info Hash (v2): {info_hash2.hex()}")
            elif info_hash2 != b'\x00' * 32:
                print(f"Info Hash (v2): {info_hash2.hex()} (长度异常: {len(info_hash2)} 字节)")

        name = data.get(b'name', b'').decode('utf-8', errors='ignore')
        if name:
            print(f"Torrent 名称: {name}")

        save_path = data.get(b'save_path', b'').decode('utf-8', errors='ignore')
        if save_path:
            print(f"保存路径: {save_path}")

        print("\n" + "=" * 80)
        print("下载进度")
        print("=" * 80)

        pieces = data.get(b'pieces', b'')
        if pieces:
            completed, total, percentage = analyze_pieces(pieces)
            print(f"已完成 pieces: {completed}/{total} ({percentage:.2f}%)")

            bits = decode_bitfield(pieces)
            if len(bits) <= 100:
                print(f"Pieces 状态: {''.join(['█' if b else '░' for b in bits])}")

        piece_priority = data.get(b'piece_priority', b'')
        if piece_priority:
            priority_counts = {}
            for byte in piece_priority:
                priority_counts[byte] = priority_counts.get(byte, 0) + 1

            print(f"\nPiece Priority 统计:")
            priority_map = {0: "不下载", 1: "低", 4: "正常", 7: "高"}
            for prio in sorted(priority_counts.keys()):
                prio_name = priority_map.get(prio, f"未知({prio})")
                print(f"  优先级 {prio} ({prio_name}): {priority_counts[prio]} 个pieces")

        verified_pieces = data.get(b'verified_pieces', b'')
        if verified_pieces:
            completed, total, percentage = analyze_pieces(verified_pieces)
            print(f"\n已验证 pieces: {completed}/{total} ({percentage:.2f}%)")

        unfinished = data.get(b'unfinished', [])
        if unfinished:
            print(f"\n未完成 pieces 数量: {len(unfinished)}")
            print(f"\n未完成 pieces 详细信息:")
            for i, piece_info in enumerate(unfinished):
                if isinstance(piece_info, dict):
                    piece_idx = piece_info.get(b'piece', -1)
                    bitmask = piece_info.get(b'bitmask', b'')
                    adler32 = piece_info.get(b'adler32', 0)

                    if bitmask:
                        bits = decode_bitfield(bitmask)
                        completed_blocks = sum(bits)
                        total_blocks = len(bits)
                        completed_percentage = (completed_blocks / total_blocks * 100) if total_blocks > 0 else 0
                        remaining_percentage = 100 - completed_percentage

                        print(f"\n  Piece {piece_idx}: (已完成 {completed_percentage:.1f}%, 未完成 {remaining_percentage:.1f}%)")
                        print(f"    已完成 blocks: {completed_blocks}/{total_blocks}")
                        print(f"    Bitmask: {''.join(['1' if b else '0' for b in bits])}")
                    else:
                        print(f"\n  Piece {piece_idx}:")

                    if adler32:
                        print(f"    Adler32 校验: {adler32}")
                else:
                    print(f"  - Piece 数据格式异常: {piece_info}")

        print("\n" + "=" * 80)
        print("Tracker 信息")
        print("=" * 80)

        trackers = data.get(b'trackers', [])
        if trackers:
            print(f"Tracker 数量: {len(trackers)}")
            for tier_idx, tier in enumerate(trackers):
                print(f"\nTier {tier_idx}:")
                if isinstance(tier, list):
                    for tracker in tier:
                        tracker_url = tracker.decode('utf-8', errors='ignore') if isinstance(tracker, bytes) else str(tracker)
                        print(f"  - {tracker_url}")

        print("\n" + "=" * 80)
        print("文件信息")
        print("=" * 80)

        file_priority = data.get(b'file_priority', [])
        if file_priority:
            print(f"文件数量: {len(file_priority)}")
            priority_map = {0: "不下载", 1: "低", 4: "正常", 7: "高"}
            for i, prio in enumerate(file_priority[:10]):
                prio_str = priority_map.get(prio, str(prio))
                print(f"  文件 {i}: 优先级 {prio_str} ({prio})")
            if len(file_priority) > 10:
                print(f"  ... 还有 {len(file_priority) - 10} 个文件")

        mapped_files = data.get(b'mapped_files', [])
        if mapped_files:
            print(f"\n重命名的文件:")
            for i, filename in enumerate(mapped_files[:10]):
                fname = filename.decode('utf-8', errors='ignore') if isinstance(filename, bytes) else str(filename)
                print(f"  {i}: {fname}")

        print("\n" + "=" * 80)
        print("统计数据")
        print("=" * 80)

        total_uploaded = data.get(b'total_uploaded', 0)
        total_downloaded = data.get(b'total_downloaded', 0)
        print(f"总上传量: {format_bytes(total_uploaded)}")
        print(f"总下载量: {format_bytes(total_downloaded)}")

        if total_downloaded > 0:
            ratio = total_uploaded / total_downloaded
            print(f"分享率: {ratio:.3f}")

        active_time = data.get(b'active_time', 0)
        seeding_time = data.get(b'seeding_time', 0)
        finished_time = data.get(b'finished_time', 0)

        print(f"活动时间: {format_time(active_time)}")
        print(f"做种时间: {format_time(seeding_time)}")
        print(f"完成时间: {format_time(finished_time)}")

        added_time = data.get(b'added_time', 0)
        completed_time = data.get(b'completed_time', 0)
        last_seen_complete = data.get(b'last_seen_complete', 0)

        print(f"添加时间: {format_timestamp(added_time)}")
        print(f"完成时间: {format_timestamp(completed_time)}")
        print(f"最后看到完整种子: {format_timestamp(last_seen_complete)}")

        print("\n" + "=" * 80)
        print("配置标志")
        print("=" * 80)

        auto_managed = data.get(b'auto_managed', 0)
        paused = data.get(b'paused', 0)
        sequential = data.get(b'sequential_download', 0)
        seed_mode = data.get(b'seed_mode', 0)
        super_seeding = data.get(b'super_seeding', 0)

        print(f"自动管理: {'是' if auto_managed else '否'}")
        print(f"暂停状态: {'是' if paused else '否'}")
        print(f"顺序下载: {'是' if sequential else '否'}")
        print(f"Seed 模式: {'是' if seed_mode else '否'}")
        print(f"Super Seeding: {'是' if super_seeding else '否'}")

        upload_limit = data.get(b'upload_rate_limit', -1)
        download_limit = data.get(b'download_rate_limit', -1)
        max_connections = data.get(b'max_connections', -1)
        max_uploads = data.get(b'max_uploads', -1)

        print(f"\n上传限速: {format_bytes(upload_limit) + '/s' if upload_limit >= 0 else '无限制'}")
        print(f"下载限速: {format_bytes(download_limit) + '/s' if download_limit >= 0 else '无限制'}")
        print(f"最大连接数: {max_connections if max_connections >= 0 else '无限制'}")
        print(f"最大上传数: {max_uploads if max_uploads >= 0 else '无限制'}")

        print("\n" + "=" * 80)
        print("Peer 信息")
        print("=" * 80)

        peers = data.get(b'peers', b'')
        if peers:
            num_peers = len(peers) // 6
            print(f"已知 IPv4 Peers: {num_peers}")

        peers6 = data.get(b'peers6', b'')
        if peers6:
            num_peers6 = len(peers6) // 18
            print(f"已知 IPv6 Peers: {num_peers6}")

        banned_peers = data.get(b'banned_peers', b'')
        if banned_peers:
            num_banned = len(banned_peers) // 6
            print(f"封禁的 Peers: {num_banned}")

        num_complete = data.get(b'num_complete', -1)
        num_incomplete = data.get(b'num_incomplete', -1)
        num_downloaded = data.get(b'num_downloaded', -1)

        if num_complete >= 0:
            print(f"完整种子数: {num_complete}")
        if num_incomplete >= 0:
            print(f"下载者数: {num_incomplete}")
        if num_downloaded >= 0:
            print(f"已完成下载次数: {num_downloaded}")

        print("\n" + "=" * 80)
        print("所有字段列表")
        print("=" * 80)

        def format_value(val, indent=2):
            """递归格式化值"""
            indent_str = " " * indent

            if isinstance(val, bytes):
                if len(val) <= 32:
                    return f"<bytes: {val.hex()}>"
                else:
                    return f"<bytes: {len(val)} 字节, hex前16字节: {val[:16].hex()}...>"
            elif isinstance(val, list):
                if len(val) == 0:
                    return "<list: 空>"
                elif len(val) <= 10:
                    result = f"<list: {len(val)} 项>\n"
                    for i, item in enumerate(val):
                        result += f"{indent_str}  [{i}]: {format_value(item, indent + 4)}\n"
                    return result.rstrip()
                else:
                    return f"<list: {len(val)} 项, 过多不展开>"
            elif isinstance(val, dict):
                if len(val) == 0:
                    return "<dict: 空>"
                else:
                    result = f"<dict: {len(val)} 项>\n"
                    for k, v in sorted(val.items()):
                        k_str = k.decode('utf-8', errors='ignore') if isinstance(k, bytes) else str(k)
                        result += f"{indent_str}  {k_str}: {format_value(v, indent + 4)}\n"
                    return result.rstrip()
            elif isinstance(val, str):
                return val
            else:
                return str(val)

        for key in sorted(data.keys()):
            key_str = key.decode('utf-8', errors='ignore') if isinstance(key, bytes) else str(key)
            value = data[key]

            if isinstance(value, bytes):
                if key in [b'info-hash', b'info-hash2', b'pieces', b'verified_pieces',
                          b'piece_priority', b'peers', b'peers6', b'banned_peers']:
                    if len(value) <= 32:
                        value_str = f"<bytes: {value.hex()}>"
                    else:
                        value_str = f"<bytes: {len(value)} 字节, hex前16字节: {value[:16].hex()}...>"
                elif len(value) > 50:
                    value_str = f"<bytes: {len(value)} 字节>"
                else:
                    try:
                        decoded = value.decode('utf-8', errors='strict')
                        if decoded.isprintable():
                            value_str = decoded
                        else:
                            value_str = f"<bytes: {value.hex()}>"
                    except:
                        value_str = f"<bytes: {value.hex()}>"
            elif isinstance(value, list):
                if key in [b'trackers', b'httpseeds', b'url-list', b'qBt-tags']:
                    value_str = f"<list: {len(value)} 项, 已在上方展示>"
                else:
                    value_str = format_value(value)
            elif isinstance(value, dict):
                value_str = format_value(value)
            else:
                value_str = str(value)

            print(f"  {key_str}: {value_str}")

        print("\n" + "=" * 80)

        return data

    except Exception as e:
        print(f"\n✗ 解析失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def find_fastresume_files(directory):
    """在指定目录中查找所有.fastresume文件"""
    fastresume_files = []

    if not os.path.exists(directory):
        print(f"错误: 目录不存在: {directory}")
        return []

    if not os.path.isdir(directory):
        print(f"错误: 不是一个目录: {directory}")
        return []

    for filename in os.listdir(directory):
        if filename.endswith('.fastresume'):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                fastresume_files.append(file_path)

    return sorted(fastresume_files)


def interactive_mode(directory):
    """交互式模式：列出目录中的所有fastresume文件供用户选择"""
    print(f"正在扫描目录: {directory}")
    print("=" * 80)

    files = find_fastresume_files(directory)

    if not files:
        print("未找到任何 .fastresume 文件")
        return

    print(f"\n找到 {len(files)} 个 fastresume 文件:\n")

    for i, file_path in enumerate(files, 1):
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        file_size_str = format_bytes(file_size)

        try:
            with open(file_path, 'rb') as f:
                data = bencodepy.decode(f.read())
            name = data.get(b'name', b'').decode('utf-8', errors='ignore')
            if name:
                print(f"  [{i:3d}] {filename}")
                print(f"        名称: {name}")
                print(f"        大小: {file_size_str}")
            else:
                print(f"  [{i:3d}] {filename} (大小: {file_size_str})")
        except:
            print(f"  [{i:3d}] {filename} (大小: {file_size_str}) [解析失败]")

        print()

    print("=" * 80)

    while True:
        try:
            choice = input("\n请输入要查看的文件编号 (输入 q 退出): ").strip()

            if choice.lower() == 'q':
                print("退出程序")
                break

            if not choice.isdigit():
                print("错误: 请输入有效的数字")
                continue

            index = int(choice)

            if index < 1 or index > len(files):
                print(f"错误: 请输入 1 到 {len(files)} 之间的数字")
                continue

            selected_file = files[index - 1]
            print("\n" + "=" * 80)
            print(f"已选择: {os.path.basename(selected_file)}")
            print("=" * 80 + "\n")

            read_fastresume(selected_file)

            print("\n" + "=" * 80)
            cont = input("\n是否继续查看其他文件? (y/n): ").strip().lower()
            if cont != 'y':
                print("退出程序")
                break

            print("\n" + "=" * 80)
            print("文件列表:")
            print("=" * 80 + "\n")
            for i, file_path in enumerate(files, 1):
                filename = os.path.basename(file_path)
                file_size = os.path.getsize(file_path)
                file_size_str = format_bytes(file_size)

                try:
                    with open(file_path, 'rb') as f:
                        data = bencodepy.decode(f.read())
                    name = data.get(b'name', b'').decode('utf-8', errors='ignore')
                    if name:
                        print(f"  [{i:3d}] {filename}")
                        print(f"        名称: {name}")
                        print(f"        大小: {file_size_str}")
                    else:
                        print(f"  [{i:3d}] {filename} (大小: {file_size_str})")
                except:
                    print(f"  [{i:3d}] {filename} (大小: {file_size_str}) [解析失败]")

                print()

        except KeyboardInterrupt:
            print("\n\n程序被中断")
            break
        except Exception as e:
            print(f"错误: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法:")
        print("  1. 解析单个文件: python read_fastresume.py <fastresume文件路径>")
        print("  2. 交互式模式:   python read_fastresume.py -d <目录路径>")
        print("\n示例:")
        print("  python read_fastresume.py /path/to/file.fastresume")
        print("  python read_fastresume.py -d /path/to/BT_backup/")
        print("  python read_fastresume.py -d ~/Library/Application\\ Support/CrossOver/Bottles/qbittorrent/drive_c/users/crossover/AppData/Local/qBittorrent/BT_backup/")
        sys.exit(1)

    if sys.argv[1] == '-d':
        if len(sys.argv) < 3:
            print("错误: 请指定目录路径")
            print("用法: python read_fastresume.py -d <目录路径>")
            sys.exit(1)

        directory = sys.argv[2]

        if directory.startswith("Support/CrossOver"):
            home = os.path.expanduser("~")
            directory = os.path.join(home, "Library/Application Support/CrossOver",
                                    directory.replace("Support/CrossOver/", ""))

        directory = os.path.expanduser(directory)
        interactive_mode(directory)
    else:
        file_path = sys.argv[1]

        if file_path.startswith("Support/CrossOver"):
            home = os.path.expanduser("~")
            file_path = os.path.join(home, "Library/Application Support/CrossOver",
                                     file_path.replace("Support/CrossOver/", ""))

        file_path = os.path.expanduser(file_path)
        read_fastresume(file_path)
