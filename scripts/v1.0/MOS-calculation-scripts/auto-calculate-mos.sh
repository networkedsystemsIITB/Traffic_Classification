rm -rf mos-scores.txt
echo "Moss score" > mos-scores.txt

for p in *.pcap
do
echo "==========================">>mos-scores.txt
echo "Name : $p" >> mos-scores.txt
sh calculate-moss.sh $p>> mos-scores.txt


done
rm c.txt n.txt a.txt
