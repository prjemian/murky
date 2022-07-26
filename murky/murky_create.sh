#!/bin/bash

# purpose: hybrid micromamba/conda environment creator

echo "$0 $@"

function usage {
    echo "usage: ${0} [-c] [-n env_name] [-y] env_file"
    echo ""
    echo "positional arguments:"
    echo "  env_file    environment YAML file"
    echo ""
    echo "optional arguments:"
    echo "  -c                Cleanup (delete) all temporary files on completion."
    echo "  --n ENVIRONMENT   Name of environment."
    echo "  -y                respond 'yes' to all prompts."
    exit
}

# ----- 1. accepts an environment file name and optional environment name

APP_DIR="$(realpath $(dirname ${0}))"
PYTOOL=$(which murky_tool)
if [ "${PYTOOL}" == "" ]; then
    PYTOOL="python3 ${APP_DIR}/murky_tool.py"
fi

if [ "$(which micromamba)" == "" ]; then
    echo "Cannot identify micromamba executable."
    exit
fi
if [ "$(which conda)" == "" ]; then
    echo "Cannot identify conda executable."
    exit
fi

environment=
yml_file=
options=
while [ -n "$1" ]; do
    case "${1}" in
        -c) CLEANUP=Yes ;;
        -n)
            if [ "${environment}" == "" ]; then
                environment=${2}
                shift
            else
                usage
            fi
            ;;
        -y) options+=" ${1}" ;;
        *)
            if [ "${yml_file}" == "" ]; then
                yml_file=${1}
            else
                usage
            fi
            ;;
    esac
    shift
done

if [ -e "${yml_file}" ]; then
    if [ "${environment}" == "" ]; then
        environment=$(${PYTOOL} name "${yml_file}")
    fi
else
    usage
fi

# echo environment=${environment}
# echo options=${options}
# echo yml_file=${yml_file}
echo "create ${options} -n ${environment} ${yml_file}"

# ----- 2. build test micromamba environment

TIMEDATE=$(date "+%H%M%S")
temp_env="_temporary_murky_env_${TIMEDATE}"
# echo temp_env=${temp_env}
micromamba create ${options} -n "${temp_env}" -f "${yml_file}"

_match=$(micromamba env list | grep "/envs/${temp_env}")
if [ "${_match}" == "" ]; then
    # What if user said NO to continue with install?  Or install failed?
    echo "Did not create temporary environment '${temp_env}'.  Stopping."
    exit
else
    micromamba env list
    echo "Activating temporary micromamba environment: ${temp_env}"
fi

eval "$(micromamba shell hook --shell=bash)"
micromamba activate "${temp_env}"
# micromamba env list

# ----- 3. create a pip requirements file from the input environment file

pip_req_file="/tmp/${TIMEDATE}_pip_req.txt"
${PYTOOL} pip "${yml_file}" | tee "${pip_req_file}"

# ----- 4. generate the explicit package list for conda

conda_explicit_file="/tmp/${TIMEDATE}_conda_explicit.txt"
conda list --explicit | tee "${conda_explicit_file}"
# Edit the environment name into the explicit file.
# $ conda create --name <env> --file <this file>
sed -i s+'<env>'+`echo "${environment}"`+g   "${conda_explicit_file}"
sed -i s+'<this file>'+`echo "${conda_explicit_file}"`+g   "${conda_explicit_file}"

# ----- 5. remove the test micromamba environment

ENV_DIR="${CONDA_PREFIX}"
echo "Removing temporary environment ${temp_env} (${ENV_DIR})"
micromamba deactivate
/bin/rm -rf "${ENV_DIR}"

# ----- 6. create named conda environment with the explicit list

echo "Creating conda environment: ${environment}"
conda create ${options} --name "${environment}" --file "${conda_explicit_file}"
echo "Activating conda environment: ${environment}"
source "${CONDA_PREFIX}/etc/profile.d/conda.sh"
conda activate "${environment}"
# conda env list
# which conda

# ----- 7. pip install remaining components in the named conda environment

line_count=($(wc -l "${pip_req_file}"))
if [ "${line_count[0]}" != "0" ]; then
    # only if requirements file is not empty
    conda env list
    $(which pip) install -r "${pip_req_file}"
fi
# ----- 8. remove pip requirements file and conda explicit file

if [ "${CLEANUP}" == "Yes" ]; then
    echo "Removing temporary conda explicit requirements file: ${conda_explicit_file}"
    echo "Removing temporary pip requirements file: ${pip_req_file}"
    /bin/rm "${pip_req_file}" "${conda_explicit_file}"
fi

# ----- 8. announce

echo ""
echo "Conda environment created.  Activate with this command:"
echo ""
echo "    conda activate ${environment}"

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     prjemian@gmail.com
# :copyright: (c) 2014-2022, Pete R. Jemian
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------
