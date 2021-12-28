import argparse
import sys

from PyQt5.QtWidgets import QApplication

from windows import GridWindow

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Segment an image into a table, recognize cells and export data."
    )
    parser.add_argument(
        "image", type=argparse.FileType("r"), help="image to be processed"
    )
    parser.add_argument(
        "--stretch",
        type=float,
        default=2,
        help="Zoom out for the segmentation value",
    )
    parser.add_argument(
        "-tlang",
        default="eng",
        help="tesseract language",
    )
    parser.add_argument(
        "-tdata",
        default=False,
        help="path to custom tesseract model files",
    )
    parser.add_argument(
        "--keepfiles",
        action="store_true",
        help="whether to keep text files and images for later training with tesseract",
    )
    parser.add_argument(
        "--debug", action="store_true", help="whether to enable debug output"
    )

    args = parser.parse_args()
    app = QApplication(sys.argv)
    tess_config = {"lang": args.tlang, "training_dir": "somelang-ground-truth"}
    if args.tdata:
        tess_config["data"] = args.tdata
    window = GridWindow(
        args.image.name,
        debug=args.debug,
        keepfiles=args.keepfiles,
        stretch=args.stretch,
        tess_config=tess_config,
    )
    window.showMaximized()
    app.exec()
