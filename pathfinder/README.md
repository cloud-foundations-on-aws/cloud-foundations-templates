# Pathfinder

Pathfinder is an open-source solution designed to provide automated discovery of AWS an environment and its multi-account architecture. The tool is intended to be executed within the AWS Management Account in the AWS CloudShell.

>**Note:** Pathfinder can operate with `READONLY` permissions **plus CloudShell permissions** to the AWS account, and does not make any changes to the AWS environment. All information generated from the tool is outputted to your local AWS CloudShell environment.

## How to Use

1. Go into an AWS account which is a `Management Account` and open CloudShell terminal (you will need the full terminal open to download the file at the end, which the full terminal takes up the whole page instead of the lower half of the page).
2. Ensure you have right now admin permissions or the proper READONLY permissions that include ability to use AWS CloudShell
    * READONLY permissions with additional permissions to run CloudShell environment.
3. Run the following command: `curl -sSL https://raw.githubusercontent.com/cloud-foundations-on-aws/cloud-foundations-templates/feat-pathfinder/pathfinder/pathfinder.sh | sh`
4. Watch screen scroll through output looking for any errors.
5. Once done you will see the tool created a directory called ./pathfinder (verify by running ls in the current working directory you are in)
6. Run cat ./pathfinder/Pathfinder.txt command to see the outputted report in console
7. Go into top right of the page and click on Actions button and click on Download File
8. In the download file enter ./pathfinder/Pathfinder.txt
9. File is download which you can now open up locally to view

## Features

* **Automated Discovery:** Pathfinder automates the discovery process, minimizing the need for manual checks and providing a quick overview of the environment.
* **READONLY Access:** The tool operates with READONLY access (**plus CloudShell permissions**) to the AWS account, ensuring that it does not make any modifications or interfere with the existing setup.
* **AWS CloudShell Compatibility:** Pathfinder is designed to be executed within AWS CloudShell, providing a convenient and secure environment for running discovery.
* **Developed in JavaScript and AWS-SDK v3:** Pathfinder is implemented using JavaScript and relies on the latest AWS-SDK v3 for seamless interaction with AWS services.

## Security Considerations

* The tool is designed to operate with READONLY access (**plus permissions to run CloudShell**), minimizing the risk of unintended changes to your environment. All data is outputted into your local CloudShell environment.
