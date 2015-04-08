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

	cd $SHELLHOME
	git submodule init
	git submodule sync
	git submodule update
	commit=`git log -1 --pretty=format:%h --no-merges`
	scsscommit=`cd $SHELLHOME/..;git ls-tree HEAD foundation-libsass-template|awk '{print $3}'|cut -c1-7`
	appjshash=`cd $SHELLHOME;git log -n 1 --pretty=format:%h -- static/js/app.js static/js/jquery.scrollUp.js`
	escortjshash=`cd $SHELLHOME;git log -n 1 --pretty=format:%h -- static/js/mobile/app.js static/js/escort/app.js static/js/escort/list.js`

	pecho "Compile mobile css"
	cd $SHELLHOME/../sass/
	grunt build
	rc=$?
	if [[ $rc != 0 ]] ; then
            perr "Failed to compile css for mobile css."
	    exit $rc
	fi

	cd $SHELLHOME
	pecho "Minifying JS files"
	npm install node-minify
	node minify.js
	rc=$?
	if [[ $rc != 0 ]] ; then
            perr "Failed to minifying JS files."
	    exit $rc
	fi

	pecho "Deploying project to DIR $TARGET..."
	cd $TARGET
	# pull latest versions
	git fetch
	git checkout -f master
	git reset --hard origin/master
	rm -rf $TARGET/*

	pecho "Clean unnecessary files..."
	cp -rf $SHELLHOME/* .
	find . -name "*.pyc" -exec rm -f {} \;
	find . -name ".git*" -exec rm -f {} \;
	rm -rf node_modules/
	rm deploy.sh
	rm *.launch
	rm bitfield
	mv django-bitfield/bitfield .
	rm -rf django-bitfield/
	rm static/js/escort/app.js static/js/escort/list.js static/js/mobile/app.js
	cp -f static/images/favicon.ico .
	cp -f billiards/settings.py.template billiards/settings.py
	pecho "Updating release version..."
        DATE=`date '+%Y%m%d'`
	DATE2=`date '+%Y.%m.%d'`
        HOUR=`date '+%H'`
        MINUTE=`date '+%M'`	
	sed -e "s/BUILDID = [1-9][0-9]*/BUILDID = $DATE$HOUR$MINUTE/g" billiards/context_processors.py | sed -e "s/REV = '[0-9]\{4\}.[0-9]\{2\}.[0-9]\{2\}.[[:alnum:]]\{6\}'/REV = '$DATE2.$commit'/g" | sed -e "s/SCSSHASH = '[[:alnum:]]\{7\}'/SCSSHASH = '$scsscommit'/g" | sed -e "s/APPJSHASH = '[[:alnum:]]\{7\}'/APPJSHASH = '$appjshash'/g" | sed -e "s/ESCORTJSHASH = '[[:alnum:]]\{7\}'/ESCORTJSHASH = '$escortjshash'/g" > billiards/context_processors.py.new
	cp -f billiards/context_processors.py.new billiards/context_processors.py
	rm -f billiards/context_processors.py.new
	pecho "Commit and push new version to BAE..."
	git add --all .
	git commit -m"Deploy new release of ibilliards"
	# increase post buffer to 50MB
	git config http.postBuffer 52428800
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
