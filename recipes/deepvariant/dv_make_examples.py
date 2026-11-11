#!/opt/anaconda1anaconda2anaconda3/bin/python
#
# Wrapper script for DeepVariant make_examples

BINARY_DIR="/opt/anaconda1anaconda2anaconda3/BINARYSUB"

import argparse
import os
import shlex
import subprocess
import sys

def real_dirname(path):
    """Return the symlink-resolved, canonicalized directory-portion of path."""
    return os.path.realpath(path)

class DVHelp(argparse._HelpAction):
    def __call__(self, parser, namespace, values, option_string=None):
        print("Baseline DeepVariant arguments")
        bin_dir = real_dirname(BINARY_DIR)
        conda_path = os.path.dirname(os.path.realpath(sys.executable))
        lib_path = os.path.join(os.path.dirname(conda_path), "lib")
        py_exe = sys.executable
        cmd = ("export LD_LIBRARY_PATH={lib_path}:\"$LD_LIBRARY_PATH\" && "
               "{py_exe} {bin_dir}/make_examples.zip --help").format(
                   lib_path=shlex.quote(lib_path),
                   py_exe=shlex.quote(py_exe),
                   bin_dir=shlex.quote(bin_dir))
        try:
            print(subprocess.check_output(cmd, shell=True))
        except subprocess.CalledProcessError as e:
            print(e.stdout.decode('UTF-8'))
        print()
        print("Wrapper arguments")
        parser.print_help()

def main():
    parser = argparse.ArgumentParser(description="DeepVariant make_examples wrapper", add_help=False)
    parser.add_argument("--cores", default=1)
    parser.add_argument("--sample", required=True, help="Sample name")
    parser.add_argument("--ref", required=True, help="Reference genome")
    parser.add_argument("--reads", required=True, help="Input BAM file")
    parser.add_argument("--regions", help="Genomic region to process")
    parser.add_argument("--logdir", required=True)
    parser.add_argument("--examples", required=True, help="Output directory for examples")
    parser.add_argument("--gvcf", help="Output directory for gvcf files. Generates output files as {{gvcf}}/{{sample}}.gvcf.tfrecord@{{cores}}.gz")
    parser.add_argument("-h", "--help", action=DVHelp)

    args = parser.parse_args()

    bin_dir = real_dirname(BINARY_DIR)
    conda_path = os.path.dirname(os.path.realpath(sys.executable))
    lib_path = os.path.join(os.path.dirname(conda_path), "lib")
    py_exe = sys.executable
    split_inputs = " ".join(str(x) for x in range(0, int(args.cores)))
    # The command is executed by a shell, so every value that comes from the
    # command line has to be quoted: an argument such as
    # --ref 'x; rm -rf ~' would otherwise start a second command.
    regions = ("--regions %s" % shlex.quote(args.regions)) if args.regions else ""
    gvcf = ("--gvcf {gvcf_dir}/{sample}.gvcf.tfrecord@{cores}.gz".format(
        gvcf_dir=shlex.quote(args.gvcf),
        sample=shlex.quote(args.sample),
        cores=shlex.quote(str(args.cores)))) if args.gvcf else ""
    cmd = ("export PATH={conda_path}:\"$PATH\" && export LD_LIBRARY_PATH={lib_path}:\"$LD_LIBRARY_PATH\" && "
           "parallel --eta --halt 2 --joblog {logdir}/log --res {logdir} "
           "{py_exe} {bin_dir}/make_examples.zip "
           "--mode calling --ref {ref} --reads {reads} {regions} "
           "{gvcf} "
           "--sample_name {sample} "
           "--examples {examples}/{sample}.tfrecord@{cores}.gz --task {{}} "
           "::: {split_inputs}").format(
               conda_path=shlex.quote(conda_path),
               lib_path=shlex.quote(lib_path),
               py_exe=shlex.quote(py_exe),
               bin_dir=shlex.quote(bin_dir),
               logdir=shlex.quote(args.logdir),
               ref=shlex.quote(args.ref),
               reads=shlex.quote(args.reads),
               regions=regions,
               gvcf=gvcf,
               sample=shlex.quote(args.sample),
               examples=shlex.quote(args.examples),
               cores=shlex.quote(str(args.cores)),
               split_inputs=split_inputs)
    sys.exit(subprocess.call(cmd, shell=True))

if __name__ == '__main__':
    main()
