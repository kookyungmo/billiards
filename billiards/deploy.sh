#!/bin/bash 

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
	pcheckopts
	STATUS=0
        SHELLHOME=`dirname $0 | sed -e 's=/\.$==g'`
        if [ "$SHELLHOME" = "." ]; then
                SHELLHOME="$PWD"
        else
                SHELLHOME=`echo $SHELLHOME | sed -e "s=^\.=$PWD/.=g"`
        fi

	pecho "Deploying project to DIR $TARGET..."
	cd $TARGET
	# pull latest versions
	git pull
	rm -rf $TARGET/*

	cp -Rfp $SHELLHOME/* .
	find . -name "*.pyc" -exec rm -f {} \;
	rm deploy.sh
	rm *.launch
	rm bitfield
	mv django-bitfield/bitfield .
	rm -rf django-bitfield/
	git add .
	git commit -m"Deploy new release of ibilliards"
	git push
		
        exit $STATUS
}

pprint ()
{
        TIMESTAMP=`date "+%d%m%y%H%M%S"`
        if [ "$VERBOSE" = "1" ]; then
                MYLOGFILE=$TMP/tmp_$TIMESTAMP.logfile
                echo "**********************************DINFO************************************" > $MYLOGFILE
                echo $* >> $MYLOGFILE
                echo "***************************************************************************" >> $MYLOGFILE
                cat $MYLOGFILE
                if [ ! "$LOGFILE" = "" ]; then
                        cat $MYLOGFILE >> $LOGFILE
                fi
                rm -f $MYLOGFILE
        else
                echo $* >> /dev/null 2>&1
        fi
}

#------------------------------pecho------------------------------------
#if $LOGFILE exists, echo and write to logfile, else simple echo!
pecho ()
{
        TIMESTAMP=`date "+%d%m%y%H%M%S"`
        MYLOGFILE=$TMP/tmp_$TIMESTAMP.logfile
        echo $* > $MYLOGFILE
        cat $MYLOGFILE
        if [ ! "$LOGFILE" = "" ]; then
                cat $MYLOGFILE >> $LOGFILE
        fi
}

pcheckopts() {
	TMP=/tmp
	pprint "Checking Options!"
        if [ "$TARGET" = "" ]; then
		perr "Option '-t' must be specified."
        fi
}

#--------------------format an error description text----------------------
# takes two arguments, first of it being short description, second long description ....
# if LOGFILE env variable exists, the output will be written to that file too!
perr()
{
        TIMESTAMP=`date "+%d%m%y%H%M%S"`
        MYLOGFILE=$TMP/tmp_$TIMESTAMP.logfile
        echo "##############################################################################" > $MYLOGFILE
        echo "--------------------------------ERROR OCCURED---------------------------------" >> $MYLOGFILE
        echo "##############################################################################" >> $MYLOGFILE
        echo "******************************************************************************" >> $MYLOGFILE
        echo "----------------------Summary :-----------------------------------------------" >> $MYLOGFILE
        echo "******************************************************************************" >> $MYLOGFILE
        echo "*                                                                                                                                                 *" >> $MYLOGFILE
        echo "*" $1 >> $MYLOGFILE
        echo "*                                                                                                                                                 *" >> $MYLOGFILE
        if [ "$VERBOSE" = "1" ];then
        echo "******************************************************************************" >> $MYLOGFILE
        echo "----------------------Long description :--------------------------------------" >> $MYLOGFILE
        echo "******************************************************************************" >> $MYLOGFILE
        echo "*                                                                                                                                                 *" >> $MYLOGFILE
        if [ -z "$2" ]; then
                echo "* No Long Description available!" >> $MYLOGFILE
        else
                for number in "$2" "$3" "$4" "$5" "$6" "$7" "$8" "$9" ; do
                if [ ! "$number" = "" ];then
                        echo "*" $number >> $MYLOGFILE
                fi
                done
        fi
        echo "*                                                                                                                                                 *" >> $MYLOGFILE
        echo "******************************************************************************" >> $MYLOGFILE
        fi
        echo "##############################################################################" >> $MYLOGFILE
        echo "----------------------------END OF DESCRIPTION, EXITING ----------------------" >> $MYLOGFILE
        echo "##############################################################################" >> $MYLOGFILE
        cat $MYLOGFILE
        if [ ! "$LOGFILE" = "" ]; then
                cat $MYLOGFILE >> $LOGFILE
        fi
        rm -f $MYLOGFILE
        exit 1
}

pusage() {
        echo "##########################################################################"
        echo "#                   USAGE of this SCRIPT (V 1.0.1)                       #"
        echo "##########################################################################"
        echo "#                                                                        #"
        echo "# This script is used to release ibiliards to BAE                        #"
        echo "#                                                                        #"
        echo "##########################################################################"
        echo "# -t DIR          ....    specify the dir to put release files into      #"
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
