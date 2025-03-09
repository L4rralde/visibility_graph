from argparse import ArgumentParser

from polygon_scene import VisibilityGraphScene


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("-c", "--complete", action="store_true")
    args = parser.parse_args()
    scene = VisibilityGraphScene("OpenGL", 900, 600, 20, complete=args.complete)
    scene.run()


if __name__ == '__main__':
    main()
