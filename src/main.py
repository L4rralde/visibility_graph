from polygon_scene import VisibilityGraphScene


def main() -> None:
    scene = VisibilityGraphScene("OpenGL", 900, 600, 20)
    scene.run()


if __name__ == '__main__':
    main()
