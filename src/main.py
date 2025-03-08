from argparse import ArgumentParser, BooleanOptionalAction

from polygon_scene import VisibilityGraphScene

def main() -> None:
    parser = ArgumentParser()
    parser.add_argument('--complete', action = BooleanOptionalAction)
    args = parser.parse_args()

    scene = VisibilityGraphScene(
        title = "OpenGL",
        width = 900,
        height = 600,
        max_fps = 20,
        complete = args.complete
    )
    scene.run()


if __name__ == '__main__':
    main()
