# Alt-I
Multiplatform OpenAI keyboard integration

# Description

This is a simple tool that integrates OpenAI ChatGPT and Davinci models by hooking the PC keyboard. It works on Linux, Mac and Windows.
It requires a OpenAI api Key, you can obtain a free evaluation Key from OpenAI by registering and then going to the user settings (https://platform.openai.com/account/api-keys)

## Installation

1. pip install alt-i

## Usage

1. Run the application: `alt-i`
2. press Alt-I in any window or shell to write the prompt. Press `esc` or `enter` to finalize the prompt. 
   The AI will automaticall answer in-line by pressing the keys.

## Example prompts:
* 'find all files starting with letter z, in subdirectories, linux command'
* 'youtube video of python tutoriar'
* 'write an example description of a github project in markup language'

Warning: The AI will sometimes write commands and execute them if you ask them to do so.

## License

This project is licensed under the BSD 2-clause License - see the [LICENSE.md](LICENSE.md) file for details.
