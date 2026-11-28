Written by tm/frontend (gpt-6.2-sol).

# Home cast render

`cast.py`, `parts.py` and `sculpt.py` are local copies of the Lilo cast block kit (`lilo-cast/b/kit`). This shot adds a folded arm pose and restages five of those rigs. `stage.py` sets their floor positions, the shared perspective camera and the light for each framing, and prints the angle, pitch and distance of each rig relative to the camera.

From the repo root, with Blender 5.1 and Python with Pillow:

```sh
Blender --background --factory-startup --disable-autoexec --python-exit-code 1 \
  --python assets/home-cast-b/source/stage.py -- /tmp/lilo-home-cast-renders
python3 -I assets/home-cast-b/source/export.py /tmp/lilo-home-cast-renders assets/home-cast-b
```

The exported WebPs store Lilo ink coverage as alpha. The page supplies the paper colour, including in the highlights and lit architecture. Only the WebPs go into the deployed static build.
