from chardet.universaldetector import UniversalDetector
def detect_encoding(file_path):
    detector = UniversalDetector()
    with UniversalDetector() as detector:
        with open(file_path, 'rb') as file:
            for line in file:
                detector.feed(line)
                if detector.done: break
    return detector.result

detect_encoding('dqi_user2.csv')