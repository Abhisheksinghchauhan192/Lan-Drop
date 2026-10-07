import subprocess


def show_qr(url):

    try:

        subprocess.run(
            [
                "qrencode",
                "-t",
                "ansiutf8",
                url
            ],
            check=True
        )

    except FileNotFoundError:

        print()
        print("qrencode not installed")
        print()
