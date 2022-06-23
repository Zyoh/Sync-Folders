from pathlib import Path
import itertools
import argparse
import shutil
import os


EPSILON: float = 0.1


def sync_directory(source_dir: Path, target_dir: Path) -> None:
	"""
	Sync target directory with source directory.
	Copies missing files from source to target.
	Deletes any files in target not present in source.
	Parameters
	----------
	source_dir: Path
		Source (reference) directory.
	target_dir: Path
		Target (affected) directory.

	"""

	source_dir: Path = Path(source_dir)
	target_dir: Path = Path(target_dir)

	# Confirm with user.
	user_consent: str = input(f"-!-!- WARNING -!-!-\nThis will alter files located in {target_dir}\nOK? (y/[N])\n> ")
	if user_consent.strip().lower() not in ["y", "yes"]:
		return

	# Delete files in target dir that aren't in this list.
	source_relative_fps: list[Path] = []

	for source_fp in source_dir.rglob("*"):
		# Convert path to new directory.
		relative_fp: Path = source_fp.relative_to(source_dir)
		target_fp: Path = target_dir / relative_fp
		# Add relative path to list.
		source_relative_fps.append(relative_fp)

		# Create if directory.
		if source_fp.is_dir():
			target_fp.mkdir(parents=True, exist_ok=True)
			continue

		# Only move if target doesn't exist or is outdated.
		if target_fp.exists():
			is_target_outdated: bool = abs(os.path.getmtime(source_fp) - os.path.getmtime(target_fp)) > EPSILON
			if not is_target_outdated:
				continue

		# Copy
		print(f"Copying {relative_fp}")
		target_fp.parent.mkdir(parents=True, exist_ok=True)
		try:
			shutil.copy2(source_fp, target_fp)
		except PermissionError:  # Ignore Windows permission errors (it works anyway?).
			pass
		except OSError:  # Ignore macOS permission errors (it works anyway?).
			pass

	# Delete files that shouldn't be there.
	for fp in target_dir.rglob("*"):
		relative_fp: Path = fp.relative_to(target_dir)
		if relative_fp not in source_relative_fps:
			if fp.is_dir():
				print(f"Deleting directory {relative_fp}")
				shutil.rmtree(fp)
			else:
				print(f"Deleting file {relative_fp}")
				fp.unlink()


def verify_sync(source_dir: Path, target_dir: Path) -> bool:
	"""
	Verify that both directories are synced by checking file paths.
	Parameters
	----------
	source_dir: Path
	target_dir: Path

	Returns
	-------
	bool
		Whether directories match.

	"""

	source_dir: Path = Path(source_dir)
	target_dir: Path = Path(target_dir)

	# All relative paths.

	relative_source_paths: list[Path] = []
	for p in source_dir.rglob("*"):
		relative_source_paths.append(p.relative_to(source_dir))

	relative_target_paths: list[Path] = []
	for p in target_dir.rglob("*"):
		relative_target_paths.append(p.relative_to(target_dir))

	# Check

	for rsp, rtp in itertools.zip_longest(relative_source_paths, relative_target_paths, fillvalue=None):
		# None only appears as fill value which means unmatched array lengths.
		# If either one is ever None, directories do not match.
		if None in (rsp, rtp):
			return False

		# If any target dir path doesn't exist in source, or vice versa, then return False.
		if rsp not in relative_target_paths or rtp not in relative_source_paths:
			return False

		source_file: Path = source_dir / rsp
		target_file: Path = target_dir / rsp

		# If only one path is a dir/file.
		if source_file.is_dir() != target_file.is_dir():
			return False

		# If either file has a different modified time.
		if not source_file.is_dir():
			if abs(os.path.getmtime(source_file) - os.path.getmtime(target_file)) > EPSILON:
				return False

	return True


def main():
	parser = argparse.ArgumentParser(
		description="Sync files from one directory to another."
	)

	parser.add_argument(
		"source",
		metavar="source",
		type=Path,
		help="Reference directory. This will be unaffected."
	)
	parser.add_argument(
		"target",
		metavar="target",
		type=Path,
		help="Target directory. This will be changed to match source directory."
	)
	parser.add_argument(
		"-V",
		action="store_true",
		help="Only verify whether two directories are synced."
	)

	args = parser.parse_args()

	if args.V:
		print(verify_sync(args.source, args.target))
	else:
		sync_directory(args.source, args.target)


if __name__ == "__main__":
	main()
