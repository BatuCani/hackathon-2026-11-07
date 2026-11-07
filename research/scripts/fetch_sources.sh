#!/usr/bin/env bash
# Fetch open-access full text (Europe PMC REST API) and clone reference repos.
# Third-party material is NOT stored in this repo; this script pulls it into research/_fetched/ (git-ignored).
set -euo pipefail
OUT="$(cd "$(dirname "$0")/.." && pwd)/_fetched"
mkdir -p "$OUT/fulltext" "$OUT/repos"

while read -r name id; do
  [ -z "$name" ] && continue
  code=$(curl -s -m 60 -o "$OUT/fulltext/$name.xml" -w '%{http_code}' \
    "https://www.ebi.ac.uk/europepmc/webservices/rest/$id/fullTextXML")
  # Non-open-access papers return an error body; drop it.
  if [ "$code" != "200" ]; then rm -f "$OUT/fulltext/$name.xml"; echo "skip $id (HTTP $code)"; else echo "ok   $id"; fi
done <<'PAPERS'
2024_Takigawa_evaluating-replay-without-ground-truth PMC11666237
2017_Trimper_caveats-coordinated-replay PMC5539192
2025_Kern_TDLM-replay-detection-challenges PMC13065329
2018_Maboudi_HMM-temporal-structure PMC6013258
2021_Denovellis_replay-at-real-world-speeds PMC8476125
2016_Box_HMM-decoding-replay PMC5097117
2016_Chen_sleep-hippocampal-ensemble-representations PMC5004124
2026_Huh_likelihood-replay PMC13469133
2026_Wu_Wei_drift-diffusion-replay PMC13614660
2018_Olafsdottir_role-of-replay PMC5847173
2019_Mackevicius_seqNMF PMC6363393
2011_LopesdosSantos_PCA-assembly-detection PMC3115970
2010_Peyrache_PCA-cell-assemblies PMC2940043
2019_Watanabe_cell-assembly-sequences PMC6554434
2016_vandeVen_offline-reactivation PMC5158132
PAPERS

for r in DavidTingley/RnR_methods Eden-Kramer-Lab/replay_trajectory_classification nelpy/nelpy \
         FeeLab/seqNMF bendor-lab/replay_detection_cross_validation \
         kemerelab/UncoveringTemporalStructureHippocampus LorenFrankLab/non_local_detector; do
  d="$OUT/repos/$(basename "$r")"
  [ -d "$d" ] || git clone --depth 1 -q "https://github.com/$r.git" "$d" && echo "cloned $r"
done
