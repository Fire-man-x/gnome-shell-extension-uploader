# Gnome shell extension - automatic uploader

This GitHub Action automatically uploads a Gnome Shell extension to the Gnome Extensions website.

## Environment Variables

The following environment variables are required for the action to work:

- `GNOME_USERNAME`: Your Gnome Extensions website username.
- `GNOME_PASSWORD`: Your Gnome Extensions website password.
- `extension_zip_file`: The path to the zip file of your Gnome Shell extension.

## Secrets

It's recommended to store your `GNOME_USERNAME` and `GNOME_PASSWORD` as secrets in your GitHub repository. You can add them in the "Secrets" section of your repository settings.

## Usage

To use this GitHub Action, you will need to create a workflow file `release.yml` in your repository's `.github/workflows` directory.

Main part of your '.yml' file

```
env:
	PROJECT_PACKAGE_NAME: "my-extension@extension-creator"
jobs:
	upload_extension:
		steps:
			-   name: Upload to GNOME Extensions
				uses: fire-man-x/gnome-shell-extension-uploader@v2
				with:
					gnome_username: ${{ secrets.GNOME_USERNAME }}
					gnome_password: ${{ secrets.GNOME_PASSWORD }}
					extension_zip_file: ./src/${{ env.PROJECT_PACKAGE_NAME }}.shell-extension.zip
```

## Full example

This example responds to the release of a version tag, e.g. `v2`.
Then it first creates a release and makes a `zip` file. Then it uploads the `zip` file to https://extensions.gnome.org/ to your account specified by your credentials `GNOME_USERNAME` and `GNOME_PASSWORD`.

Here is an example content of file and how to set it up:

```
name: Create release and package CI

on:
	push:
		tags:
			- 'v*'

env:
	PROJECT_PACKAGE_NAME: "my-extension@extension-creator"

jobs:
	create_release:
		runs-on: ubuntu-latest

		steps:
			-   name: Checkout code
				uses: actions/checkout@v4

			-   name: Install dependencies
				run: |
					sudo apt-get update > /dev/null
					sudo apt-get install -y gnome-shell-extensions gettext > /dev/null

			-   name: Run prepare job
				run: |
					echo "Running prepare_job"
					cd src
					gnome-extensions pack

			-   name: Create GitHub Release
				id: create_release
				uses: actions/create-release@v1.1.4
				env:
					GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
				with:
					tag_name: ${{ github.ref }}
					release_name: 'Release ${{ github.ref_name }}'
					body: 'Release ${{ github.ref_name }}'
					draft: false
					prerelease: false

			-   name: Upload ZIP to Release
				uses: actions/upload-release-asset@v1.0.2

				env:
					GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
				with:
					upload_url: ${{ steps.create_release.outputs.upload_url }}
					asset_path: ./src/${{ env.PROJECT_PACKAGE_NAME }}.shell-extension.zip
					asset_name: gnome-shell-extension.zip
					asset_content_type: application/zip

			-   name: Upload artifact
				uses: actions/upload-artifact@v4
				with:
					name: shell-extension-artifact
					path: src/${{ env.PROJECT_PACKAGE_NAME }}.shell-extension.zip

	upload_extension:
		runs-on: ubuntu-latest
		needs: create_release


		steps:
			-   name: Checkout code
				uses: actions/checkout@v4

			-   name: Download artifact
				uses: actions/download-artifact@v4
				with:
					name: shell-extension-artifact
					path: src/

			-   name: Verify extension.zip exists
				run: if [ -f "./src/${{ env.PROJECT_PACKAGE_NAME }}.shell-extension.zip" ]; then echo "File exists"; else echo "File not found"; exit 1; fi

			-   name: Upload to GNOME Extensions
				uses: fire-man-x/gnome-shell-extension-uploader@v2
				with:
					gnome_username: ${{ secrets.GNOME_USERNAME }}
					gnome_password: ${{ secrets.GNOME_PASSWORD }}
					extension_zip_file: ./src/${{ env.PROJECT_PACKAGE_NAME }}.shell-extension.zip
```