Written by tm/frontend (gpt-6.2-sol).

# Home cast render

`cast.py`, `parts.py` and `sculpt.py` are local copies of the Lilo cast block kit (`lilo-cast/b/kit`). This shot restages five rigs and adds the folded arms, Kern's arm swing and Sill's departing walk. `stage.py` sets their floor positions, the shared low perspective camera and the doorway light for each framing. It prints the camera height and tilt and the angle, pitch and distance of each rig relative to the camera.

From the repo root, with Blender 5.1 and Python with Pillow:

```sh
Blender --background --factory-startup --disable-autoexec --python-exit-code 1 \
  --python assets/home-cast-b/source/stage.py -- /tmp/lilo-home-cast-renders
python3 -I assets/home-cast-b/source/export.py /tmp/lilo-home-cast-renders assets/home-cast-b
```

The rendered floor catches shadows on a transparent background. `export.py` fades the far ends of those shadows into the page and stores the blend as ink coverage. The page supplies the paper colour. Only the responsive WebPs go into the deployed static build.
