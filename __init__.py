import fiftyone.operators as foo
import fiftyone.operators.types as types
import fiftyone.core.utils as fou

class ToFramesOperator(foo.Operator):
    @property
    def config(self):
        return foo.OperatorConfig(
            name="to-frames-operator",
            label="Export video frames (to_frames)",
            description="Wraps the `to_frames` method and exposes its parameters",
            # Hide from operator browser if you only want to trigger it from code/panel
            unlisted=False,
            # Optionally allow delegated (background) execution
            allow_delegated_execution=True,
            allow_immediate_execution=True,
        )

    def resolve_input(self, ctx):
        """
        Builds the input form so that the user can configure all `to_frames`
        parameters before running the operator.
        """
        inputs = types.Object()

        # Boolean flags
        inputs.bool(
            "sample_frames",
            label="sample_frames",
            description="Re-sample video frames (True) or use existing frames (False)?",
            default=False
        )
        inputs.bool(
            "sparse",
            label="sparse",
            description="Sample only frames whose `Frame` objects already exist in the dataset?",
            default=False
        )
        inputs.bool(
            "force_sample",
            label="force_sample",
            description="Whether to resample frames that already exist on disk",
            default=False
        )
        inputs.bool(
            "skip_failures",
            label="skip_failures",
            description="Continue gracefully if a video cannot be sampled?",
            default=True
        )
        inputs.bool(
            "verbose",
            label="verbose",
            description="Log information about frames that will be sampled?",
            default=False
        )

        # Numeric fields (float/int)
        # If left blank, user can keep them None
        inputs.float(
            "fps",
            label="fps",
            description="Frame rate at which to sample frames (None to skip)",
            required=False
        )
        inputs.float(
            "max_fps",
            label="max_fps",
            description="Maximum frame rate above which frames are downsampled (None to skip)",
            required=False
        )

        # size, min_size, max_size can be tuples (width, height).  We'll let
        # the user type something like '640, 480' or '-1, 720', etc. 
        # A simple approach is to accept text and parse it in execute().
        inputs.str(
            "size",
            label="size (width, height)",
            description="e.g. '640, 480' or '-1, 720'. Leave blank to skip",
            required=False
        )
        inputs.str(
            "min_size",
            label="min_size (width, height)",
            description="e.g. '320, 240' or '-1, 240'. Leave blank to skip",
            required=False
        )
        inputs.str(
            "max_size",
            label="max_size (width, height)",
            description="e.g. '1280, 720' or '-1, 1080'. Leave blank to skip",
            required=False
        )

        # String fields
        inputs.str(
            "output_dir",
            label="output_dir",
            description="Path to directory in which to write frames. (Optional)",
            required=False
        )
        inputs.str(
            "rel_dir",
            label="rel_dir",
            description="Relative directory to remove from video filepaths, if possible",
            required=False
        )
        inputs.str(
            "frames_patt",
            label="frames_patt",
            description="Filename pattern (e.g. '%06d.jpg'). Leave blank for default",
            required=False
        )

        return types.Property(inputs, view=types.View(label="to_frames parameters"))

    def execute(self, ctx):
        """
        Reads user inputs from `ctx.params` and calls `ctx.view.to_frames()` using them.
        """
        params = ctx.params

        # Helper to parse "640,480" style string into (w, h) int tuple
        def _parse_wh(s):
            if not s:
                return None
            s = s.strip()
            if not s:
                return None
            parts = [p.strip() for p in s.split(",")]
            if len(parts) != 2:
                raise ValueError(f"Invalid width,height string: '{s}'")
            return (int(parts[0]), int(parts[1]))

        # Convert text fields to the appropriate types or None
        size_val = _parse_wh(params.get("size", None))
        min_size_val = _parse_wh(params.get("min_size", None))
        max_size_val = _parse_wh(params.get("max_size", None))

        # `fps` and `max_fps` are floats or None
        fps_val = params.get("fps", None)
        max_fps_val = params.get("max_fps", None)

        # Convert empty strings to None, etc.
        output_dir = params.get("output_dir", None) or None
        rel_dir = params.get("rel_dir", None) or None
        frames_patt = params.get("frames_patt", None) or None

        # Boolean flags
        sample_frames = bool(params.get("sample_frames", False))
        sparse = bool(params.get("sparse", False))
        force_sample = bool(params.get("force_sample", False))
        skip_failures = bool(params.get("skip_failures", True))
        verbose = bool(params.get("verbose", False))

        # Actually invoke to_frames
        frames_view = ctx.view.to_frames(
            sample_frames=sample_frames,
            fps=fps_val if fps_val is not None else None,
            max_fps=max_fps_val if max_fps_val is not None else None,
            size=size_val,
            min_size=min_size_val,
            max_size=max_size_val,
            sparse=sparse,
            output_dir=output_dir,
            rel_dir=rel_dir,
            frames_patt=frames_patt,
            force_sample=force_sample,
            skip_failures=skip_failures,
            verbose=verbose,
        )

        # For demonstration, return the total number of frames 
        # that ended up in the resulting FramesView
        return {"num_frames": len(frames_view)}

    def resolve_output(self, ctx):
        """
        After execution completes, display a read‐only summary to the user.
        """
        outputs = types.Object()
        outputs.int(
            "num_frames",
            label="Number of frames generated",
            description="Total frames in the returned FramesView",
        )
        return types.Property(outputs, view=types.View(label="to_frames summary"))

def register(p):
    p.register(ToFramesOperator)
