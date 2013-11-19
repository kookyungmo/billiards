#!/bin/bash -x

pgetopt(){
        case $1 in
                t)
                        TARGET=$OPTARG
                        ;;
                v)
                        VERBOSE=1
                        ;;
        esac
}

main(){
	STATUS=0
        SHELLHOME=`dirname $0 | sed -e 's=/\.$==g'`
        if [ "$SHELLHOME" = "." ]; then
                SHELLHOME="$PWD"
        else
                SHELLHOME=`echo $SHELLHOME | sed -e "s=^\.=$PWD/.=g"`
        fi

	rm -rf $TARGET/*
	cd $TARGET

	cp -Rfp $SHELLHOME/* .
	find . -name "*.pyc" -exec rm -f {} \;
	rm *.launch
	rm bitfield
	mv django-bitfield/bitfield .
	rm -rf django-bitfield/
	git add .
	git commit -m"Deploy new release of ibilliards"
	git push
		
        exit $STATUS
}

#########
# Do it #
#########
while getopts t: option
do
        case $option in
                \?)
                        pusage
                        echo "Incorrect usage!"
                        echo "One or more arguments are not understood by this shell!"
                        exit 1
                        ;;
        esac
        pgetopt $option pgetopt $option
done
main
