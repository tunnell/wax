Search.setIndex({envversion:43,filenames:["jargon","usage","history","modules","cito.Trigger","profiling","contributing","readme","cito.EventBuilder","cito","data_format","cito.core","index","authors","installation"],titles:["Jargon","Usage","History","cito","cito.Trigger package","Notes on code speed and profiling","Contributing","Code for Intelligent Triggering Online","cito.EventBuilder package","cito package","Data formats","cito.core package","Welcome to Code for Intelligent Triggering Online&#8217;s documentation!","Credits","Installation"],objnames:{"0":["py","module","Python module"],"1":["py","method","Python method"],"2":["py","class","Python class"],"3":["py","function","Python function"],"4":["py","attribute","Python attribute"],"5":["py","staticmethod","Python static method"]},titleterms:{inspector:9,intellig:[7,12],python3:14,dboper:9,bug:6,task:8,subpackag:9,core:[8,11],get:6,fix:6,document:[6,12],note:5,request:6,featur:[7,6],snappi:14,compil:14,packag:[8,9,11,4],format:10,feedback:6,implement:6,main:11,peakfind:4,output:[8,10],type:6,pull:6,trigger:[7,12,4],system:14,credit:13,develop:13,linear:14,onlin:[7,12],math:11,librari:14,waveform:11,fortran:14,content:[5,11,9,8,4],write:6,welcom:12,line:5,prepar:14,report:6,instal:14,indic:12,speed:5,submodul:[8,9,11,4],eventbuild:8,scipi:14,lead:13,tabl:12,depend:14,logic:8,numpi:14,contributor:13,databas:14,per:5,xedb:11,profil:5,contribut:6,histori:2,environ:14,modul:[8,9,11,4],jargon:0,python:14,input:10,submit:6,tip:6,usag:1,option:14,algebra:14,start:6,code:[5,7,12],cito:[3,4,8,9,11,14],guidelin:6,data:10,own:14,filebuild:9,mongodb:14,time:5,hit:5},objects:{"":{cito:[9,0,0,"-"]},"cito.Inspector.InputDBInspector":{helper:[9,1,1,""],take_action:[9,1,1,""],formatter2:[9,5,1,""],re_range:[9,1,1,""]},"cito.EventBuilder":{ProcessToMongoCommand:[8,2,1,""],Tasks:[8,0,0,"-"],Output:[8,0,0,"-"],Logic:[8,0,0,"-"]},"cito.FileBuilder":{FileBuilderCommand:[9,2,1,""]},cito:{Inspector:[9,0,0,"-"],FileBuilder:[9,0,0,"-"],EventBuilder:[8,0,0,"-"],Trigger:[4,0,0,"-"],DBOperations:[9,0,0,"-"],core:[11,0,0,"-"]},"cito.core.main.CitoCommand":{get_tasks:[11,1,1,""],take_action_wrapped:[11,1,1,""],get_parser:[11,1,1,""],take_action:[11,1,1,""],get_description:[11,1,1,""]},"cito.EventBuilder.Output.MongoDBOutput":{write_events:[8,1,1,""],mongify_event:[8,1,1,""]},"cito.EventBuilder.Tasks":{ProcessTimeBlockTask:[8,2,1,""]},"cito.EventBuilder.Output.OutputCommon":{write_event:[8,1,1,""],event_number:[8,4,1,""]},"cito.DBOperations.DBReset":{take_action:[9,1,1,""]},"cito.DBOperations.DBRepair":{take_action:[9,1,1,""]},"cito.DBOperations.DBPurge":{take_action:[9,1,1,""]},"cito.core":{main:[11,0,0,"-"],Waveform:[11,0,0,"-"],math:[11,0,0,"-"],XeDB:[11,0,0,"-"]},"cito.core.main.CitoShowOne":{get_status:[11,1,1,""],get_parser:[11,1,1,""],get_description:[11,1,1,""],log:[11,4,1,""]},"cito.EventBuilder.Logic.EventBuilder":{build_event:[8,1,1,""],get_event_number:[8,1,1,""]},"cito.core.main.CitoContinousCommand":{get_tasks:[11,1,1,""],take_action_wrapped:[11,1,1,""],get_parser:[11,1,1,""]},"cito.core.Waveform":{get_samples:[11,3,1,""],get_data_and_sum_waveform:[11,3,1,""]},"cito.EventBuilder.ProcessToMongoCommand":{get_tasks:[8,1,1,""]},"cito.EventBuilder.Tasks.ProcessTimeBlockTask":{process:[8,1,1,""]},"cito.EventBuilder.Output":{OutputCommon:[8,2,1,""],MongoDBOutput:[8,2,1,""]},"cito.Trigger":{PeakFinder:[4,0,0,"-"]},"cito.DBOperations":{DBReset:[9,2,1,""],DBPurge:[9,2,1,""],DBRepair:[9,2,1,""]},"cito.core.main.CitoSingleCommand":{take_action_wrapped:[11,1,1,""]},"cito.core.main":{main:[11,3,1,""],CitoContinousCommand:[11,2,1,""],CitoCommand:[11,2,1,""],CitoSingleCommand:[11,2,1,""],CitoShowOne:[11,2,1,""],CitoApp:[11,2,1,""]},"cito.Trigger.PeakFinder":{find_peaks:[4,3,1,""],identify_nonoverlapping_trigger_windows:[4,3,1,""]},"cito.EventBuilder.Logic":{find_sum_in_data:[8,3,1,""],EventBuilder:[8,2,1,""]},"cito.core.main.CitoApp":{prepare_to_run_command:[11,1,1,""],initialize_app:[11,1,1,""],clean_up:[11,1,1,""]},"cito.core.math":{merge_subranges:[11,3,1,""],overlap_region:[11,3,1,""],overlap:[11,3,1,""],compute_subranges:[11,3,1,""],find_subranges:[11,3,1,""]},"cito.FileBuilder.FileBuilderCommand":{get_parser:[9,1,1,""],take_action:[9,1,1,""],get_description:[9,1,1,""]},"cito.Inspector.OutputDocInspector":{get_parser:[9,1,1,""],take_action:[9,1,1,""]},"cito.Inspector.InputDocInspector":{get_parser:[9,1,1,""],take_action:[9,1,1,""]},"cito.Inspector":{OutputDocInspector:[9,2,1,""],InputDocInspector:[9,2,1,""],InputDBInspector:[9,2,1,""]},"cito.core.XeDB":{get_min_time:[11,3,1,""],get_max_time:[11,3,1,""],get_mongo_db_objects:[11,3,1,""],get_sort_key:[11,3,1,""],get_data_docs:[11,3,1,""],get_pymongo_collection:[11,3,1,""],get_server_name:[11,3,1,""],get_data_from_doc:[11,3,1,""]}},objtypes:{"0":"py:module","1":"py:method","2":"py:class","3":"py:function","4":"py:attribute","5":"py:staticmethod"},terms:{python3:12,open:[7,6,10],differ:8,min_tim:11,item:10,get:11,review:10,document:[11,9],iter:11,hit:12,start:[11,9],mayb:[5,9,10],convolv:4,hand:5,mongify_ev:8,adv:14,web:6,hint:14,through:[11,6],experi:7,add:[6,14],index:[11,12,9],point:[14,4],run:[1,6,9,14,4],adc:[10,9,4],within:[8,14,11,4],"import":10,physic:7,check:[5,6,11,8],get_data_from_doc:11,fail:[5,2],ctunnel:13,xedb:9,"boolean":8,comput:7,citoapp:11,now:[6,10],echo:14,zero:9,delet:9,recommend:[6,14],main:[8,9],much:9,non:9,charg:[8,10],regain:9,after:[8,9],dure:[8,9],creation:10,queri:[5,11,8],correspond:[0,8],reduc:14,divid:11,longer:11,problem:14,cito_fil:10,fkrull:14,n_sampl:11,schema:[11,10],slow:9,take:[8,11],make:[6,14,10],process:[0,7,8,5],width:4,littl:[6,14],cliff:[11,9],think:8,given:[6,10,14,4],identif:4,upper:10,dist:14,howev:[14,10],find_subrang:11,field:10,articl:6,list:[11,6,14,4],bootstrap:14,filter:[2,4],also:[8,14],which:[10,14,4],logger:11,seen:11,per:[11,12,10],where:[8,1,10,4],other:[8,6,9],download:14,atla:14,inspect:9,replac:9,integ:11,more:[8,6],bitbucket:14,program:[11,14],fork:6,form:10,ylabel:10,action:11,found:[5,4],chang:6,number:[5,10,11,8],file:[6,10,2,9],core:9,out:8,discard:8,here:[8,6,14,10],label:10,argument:[2,9],max1:11,git:6,profil:12,how:[8,6,9,11],gfortran:14,"static":9,therefor:[14,10],provid:8,v1724:[7,9],complic:14,still:8,befor:[8,6],easi:14,grab:9,tunnel:[7,6,13],end:9,relev:8,"7f0ceb10":14,entir:2,christoph:13,from:[2,8,9,10,11,14],peak:[8,10,11,4],must:[5,14,11,10],quicker:14,oper:[8,6,9,11],zip:10,checkout:6,html:11,waveform:[8,9,4],show:[11,9,10],scitool:14,portabl:14,speed:12,easier:6,rang:[0,4,8,10,11,14],"0x10bd83e50":11,statist:9,mongodboutput:8,propos:6,min2:11,min1:11,descript:[11,6],step:[6,9,10],down:9,breur:13,command:[11,1,2,14,9],singl:[7,9],sinc:[8,11],event_build:5,peakfind:9,restart:14,refer:[0,14],beforehand:10,over:[11,7,2,14],els:5,get_min_tim:11,window:[8,7,2,4],num:11,issu:6,build_ev:[5,8],post:6,nikhef:13,eventbuild:9,your:6,datalength:10,showon:11,take_action_wrap:11,depend:12,"true":[8,10],write_ev:[5,8],server:[11,14],print:9,drift:0,usag:12,variabl:[8,11,10],ez_setup:14,volunt:6,"switch":2,tupl:11,data_doc:5,search:12,store:11,misplac:2,pad:[5,11],first:[7,4],deb:14,databas:[8,12,9,11,10],usabl:10,get_pars:[11,9],noth:14,get_task:[8,11],thread:7,get_sampl:11,find_sum_in_data:8,close:10,dev:14,complet:14,includ:[8,6],work:6,t_post:8,algorithm:8,word:8,setup:[11,6],get_mongo_db_object:11,onlin:6,convolut:2,help:6,have:[7,14,10],openssh:14,cmd:11,would:6,your_name_her:6,cwt_width:4,get_data_doc:[5,11],essenti:14,"525186149d7a330faeae9d68":10,"525186149d7a330faeae9d65":10,backend:7,explain:6,input:[8,9,11],"_build":11,two:[8,4],rememb:6,pyplot:10,convert:[8,10],citocommand:11,than:11,celeri:7,turn:0,helper:9,filebuildercommand:9,troubleshoot:6,prog_nam:[11,9],logic:9,doctre:11,servic:14,pklz:10,libatla:14,environ:12,matplotlib:[14,10],when:[6,14,10],inputdbinspector:9,routin:14,combin:11,small:[9,14],otherwis:11,app_arg:[8,9,11],seper:4,fetch:11,rais:[5,11,8],attempt:14,debug:5,titl:10,etc:14,even:6,pair:11,onc:[14,4],sudo:14,finder:4,data_format:11,want:[6,9],sampl:[8,10,11,4],googl:14,sum:[8,10,11,4],independ:8,range_around_peak:11,sequenti:8,figur:10,size:[5,14,11],data:[8,9,11],about:[6,9,10],objectid:10,year:10,group:11,push:6,libsnappy1:14,ital:14,bern:2,docstr:6,determin:11,stackoverflow:11,actual:[10,4],licens:7,meet:6,paramet:[8,11],except:5,onli:[5,14,11,10],connect:11,memori:9,"_id":10,rate:7,access:11,larger:11,math:9,decompress:[11,9],occur:[8,2,11],processtomongocommand:8,activ:14,four:10,astroparticl:7,inputdocinspector:9,simpl:9,count:[10,4],"class":[8,9,11,4],pull_request:6,error:11,offici:6,wrap:11,address:11,ani:[11,6],find_peak:4,self:5,citoshowon:[11,9],wai:6,ridg:4,org:[6,14],compress:[8,9,14,10],them:[11,6],record:8,thei:[6,9],saniti:[5,8],mai:[8,10],alpha:2,valu:[8,4],question:11,observ:14,reset:9,overflow:10,pymongoerror:11,max:11,block:[0,7,9,11,8],done:6,defin:[8,9,4],look:[11,6],type:[8,11],tox:6,code:6,merge_subrang:11,avoid:14,outputcommon:8,keep:[8,6],find:[8,4],fuction:11,option:[12,2],nosql:10,pickl:[8,10],alwai:6,too:9,move:9,releas:2,itself:14,payload:[11,10],pass:6,get_descript:[11,9],numer:7,output:9,sort:11,easy_instal:14,cannot:9,hostnam:8,around:[11,10],typic:[0,8,4],doc:[11,6,14,10],doe:11,ppa:14,contigu:0,citocontinouscommand:[8,11],don:[8,9],upstart:14,formatter2:9,applic:11,blog:6,intellig:6,requir:[10,14,4],maximum:[0,11],beta:2,dictionari:11,send:[6,14],reproduc:6,def:5,anyth:6,subsequ:8,put:6,travi:6,trigger:[8,9],take_act:[11,9],postprocess:8,test:[6,2,14],entri:4,initi:[5,11,8],contin:[9,4],tmp:14,name:[11,6,14],str:[11,10],note:12,understand:11,assertionerror:[5,11,8],unit:11,plt:10,subset:6,contain:[11,9,10],distribut:7,support:6,data2:10,lst:9,current:11,dep:14,"return":[5,11,8,4],mongo:[11,10],major:2,present:1,subrang:4,interfac:[11,1,9],copi:[6,9],prepare_to_run_command:11,kei:[11,14,10],unus:9,github:[7,6,14],sure:[6,14],framework:7,everi:[6,14],prepar:12,bugfix:6,cpu:14,base:[8,14,2,11,9],plot:10,space:9,wavelet:4,need:14,flash:9,perform:[8,11,4],introduc:4,pymongo:11,minimum:11,project:6,outputdocinspector:9,event_data:8,none:[8,11],enough:[9,10],repo:[6,14],network:14,detail:[8,6],unsmooth:10,bin:14,repair:9,just:[5,6],necessari:11,clock:10,bit:[11,6,10],fals:8,construct:8,scientif:14,bold:14,octob:10,keyserv:14,distanc:11,between:[5,11],old:9,associ:2,continu:[8,11],free:7,format:11,daq:[0,9,8],arrai:[8,4],distinct:8,get_index_mask_for_trigg:8,narrow:6,specif:[8,11],http:[11,7,6,14],"default":[8,9],instruct:[6,14],goal:7,instal:[6,12],recv:14,clean_up:11,"function":[11,6,4],creat:[8,6,10],purg:9,dict:[8,11],smooth:10,param:5,slice:8,deadsnak:14,pypa:14,scope:6,overlap_region:11,cursor:[5,11],possibl:[8,6,1,14],mean:11,t_pre:8,spacial:4,threshold:[5,7,4],each:[8,10],citoenv:14,order:[11,14],transfer:14,abl:[7,9],what:9,select:11,get_sort_kei:11,get_data_and_sum_waveform:[5,11],wget:14,len:5,separ:8,distro:14,line:[9,12,2,14,4],handl:11,citosinglecommand:11,tee:14,reli:9,driven:6,"try":5,dbpurg:9,app:[8,9,11],inspir:14,fragment:9,apt:14,numberint:10,exampl:[8,10,11,4],tag:6,chunk_siz:11,queue:7,thu:8,jargon:[8,12],python:[8,6,12],repositori:14,sander:13,potenti:14,re_rang:9,multipl:4,vline:10,detector:[0,8],"new":[6,9],"final":[5,11,8],butter:[2,4],thi:[0,7,4,5,6,10,9,8,11,14],contig:[8,4],earliest:8,concept:14,get_server_nam:11,allow:4,triggertim:10,setuptool:14,page:12,snappi:10,know:[5,9,8],clone:6,later:14,caen:[11,7,10],all:[8,6,9,10,11,14],own:12,valueerror:8,board:[8,11,10],save:8,been:[11,14],legend:10,xlabel:10,skip:[8,14],ylim:10,scale:7,common:11,mani:[11,6],event:[0,5,8,9,10,11],numberlong:10,collect:[11,9],locat:11,forward:4,local:6,due:[2,14],range1:11,specifi:9,annoi:14,range2:11,arg:[11,4],get_pymongo_collect:11,event_numb:8,max2:11,channel:[8,11,10],readm:6,get_max_tim:11,task:9,less:11,libsnappi:14,drop:9,compute_subrang:11,behind:14,normal:14,read:[8,2,10],binari:10,backward:4,without:9,dbrepair:9,build:[0,14,9,8,5],you:[6,1,14,10],mock:5,latest:8,set:[8,6,11],event_data_list:8,time:[12,0,10,11,8],call:[8,9],pileup:8,ubuntu:14,see:[8,1,11],virtualenv:[6,14],exist:[9,14],few:7,refactor:2,merg:[11,9],predefin:8,branch:6,welcom:6,screen:14,peak_i:8,peak_k:8,technic:8,pmt:8,bsd:7,expans:2,left:8,system:[6,12,10],advis:14,readi:6,can:[1,5,6,9,8,11,14],cap:14,overlap:11,might:6,load:10,websit:6,invert:11,unittest:6,some:[8,2,14,11],explicitli:14,err:11,scalabl:7,log:[5,11],till:11,follow:[8,14],todo:[5,9,14,11],test_cito:6,write:8,"break":8,inform:[8,9],basic:14,parsed_arg:[8,9,11],whoever:6,"int":[5,11,8,4],best:6,should:[6,9],jewish:10,user:[8,14],appreci:6,chunk:[5,8],object:[8,11],particl:[0,7,8],updat:[6,14],digit:[8,10],pre:7,initialize_app:11,analyz:[5,9,11],interact:[0,8],mongodb:[8,12,9,11],pleas:[6,14],softwar:[7,14],argv:11,builtin:8,intend:7,individu:8,writer:9,whether:6,further:8,kill:9,sourc:[7,4,8,9,11,14],warn:[5,9],abov:[8,10,4],repres:8,rst:6,constitut:7,flake8:6,lower:10,inserts:10,though:9,identifi:[8,11,10],"10gen":14,get_event_numb:8,"byte":[5,11,8],flexibl:7,track:8,indic:[8,10,11,4],made:14,get_statu:11,expens:9,could:6,"float":4,gzip:10,origin:6,raw:[8,14,10],commit:6,result:[11,2],calendar:10,dbreset:9,com:[11,6,14],identify_nonoverlapping_trigger_window:4,adjac:11,version:[11,6],sanderb:13,wide:14,greatli:6,bson:10,properti:14,pip:[6,14],processtimeblocktask:8,part:6,offset:[11,4]}})