from argparse import ArgumentParser

from polygon_scene import VisibilityGraphScene

def parse_args() -> object:
    parser = ArgumentParser()

    parser.add_argument(
        "--complete",
        action = "store_true",
        help = "Muestra todos los vértices: grafo de visibilidad completo"
    )
    parser.add_argument(
        "--width",
        default = 720,
        type = int,
        help = "Ancho en píxeles de la ventana"
    )
    parser.add_argument(
        "--height",
        default = 480,
        type = int,
        help = "Altura en píxeles de la ventana"
    )
    parser.add_argument(
        "--fps",
        default = 20,
        type = int,
        help = "FPS de la simulación"
    )

    args = parser.parse_args()
    return args

def main() -> None:
    args = parse_args()

    if args.complete:
        title = "Visibility Graph"
    else:
        title = "Reduced Visibility Graph"

    scene = VisibilityGraphScene(
        title = title,
        width = args.width,
        height = args.height,
        max_fps = args.fps,
        complete = args.complete
    )
    scene.run()


if __name__ == '__main__':
    main()
