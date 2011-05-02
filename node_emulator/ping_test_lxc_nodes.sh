for i in 10.66.1.2 10.66.2.1 10.66.1.3 10.66.2.2  172.16.2.223  10.66.1.1;
do
    for y in 10.66.1.2 10.66.2.1  10.66.1.3 10.66.2.2  172.16.2.223  10.66.1.1;
    do
	[ "$i" == "$y" ] && continue
	ssh -q firelet@$i "ping -q $y -w1 -i.2 >/dev/null && echo $i - $y ok || echo $i - $y unreach" &
    done
done    | sort
wait
