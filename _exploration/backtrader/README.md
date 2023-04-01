## Environment Setup

conda create -n backtrader-py38 python=3.8

conda activate backtrader-py38

pip install -r requirements.txt

pip install git+https://github.com/happydasch/btoandav20

---- remove conda env ----

conda deactivate

conda env remove -n backtrader-py38


---- jupyter kernel ----

python -m ipykernel install --user --name=backtrader-py38
jupyter kernelspec list
jupyter kernelspec remove abc


---- archived ----
pip install git+https://github.com/oanda/oandapy.git
