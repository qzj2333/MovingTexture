/*
 *Read four pgm img file and output a ppm img file that has BCL times larger than
 *input file. Each BCL * BCL region was 4 values from four input files, each value
 *has SCL * SCL size.
 */

#include <fstream>
#include <iostream>
#include <sstream>
#include <string.h>
#include <cstdlib> 
#include <ctime> 
#include <math.h>

#define BCL 10
#define SCL 5 
#define LMIN 53
#define LMAX 95
#define STEPS 255

using namespace std;

const double Kappa = 903.3; // Intent is 24389/27
const double Epsilon = 0.008856;

//Debug
// if you get negative color check out fact in the getcolor, make sure fact hass  a float number assigne dto it

// fourByfour Random assignments 
// (If you want random assignment comment the following line ----
// ----> myRand[0]=0; myRand[1]=1; myRand[2]=2; myRand[3]=3;

// Input: 4 pgm files (skip .pgm) corresponding to the four variables. 
// e.g. 11_vap 11_tmn 11_pre 11_wnd

// Output: outf_10by10.ppm, displaing the four variables in a 
//         10x10 pixel box, in which each 5x5 smaller box
//         represents one of the four variables   

// The pgm files have been Histeq in matlab, see  mymatlab.txt
// the pieces are already cut out from the world data and 
// there is no need to scale them down or up

// Four colors have been chosen in LAB color space but will be changed
// 1) From (L=62, 33,  -7)  to (97, 4, -1)
// 2) From (L=62, 10,  -32) to (97, 1, -4)
// 3) From (L=62, -33, 7)   to (97, -4, 1)
// 4) From (L=62, 23,  25)  to (97, 3, 3)

// LAB->XYZ->RGB color conversion are from 
// http://www.easyrgb.com/index.php?X=MATH&H=08#text8

int nred=0, ngreen=0, nblue=0, tst=0; //For debugging

void convertLabToXyz(float L, float a, float b, float *X, float *Y, float *Z)
{

	float var_Y, var_X, var_Z;

	double ref_X =  95.047;
	double ref_Y = 100.000;
	double ref_Z = 108.883;

	var_Y = ( L + 16.0 ) / 116.0;
	var_X = a / 500.0 + var_Y;
	var_Z = var_Y - b / 200.0;

	if ( L > Epsilon * Kappa )
		var_Y = pow(var_Y,3);
	else
		var_Y = ( var_Y - 16.0 / 116.0 ) / 7.787;

	if ( pow(var_X,3) > 0.008856 )
		var_X = pow(var_X,3);
	else
		var_X = ( var_X - 16.0 / 116.0 ) / 7.787;

	if ( pow(var_Z,3) > 0.008856 )
		var_Z = pow(var_Z,3);
	else
		var_Z = ( var_Z - 16.0 / 116.0 ) / 7.787;

	*X = ref_X * var_X;     //ref_X =  95.047     Observer= 2? Illuminant= D65
	*Y = ref_Y * var_Y;     //ref_Y = 100.000
	*Z = ref_Z * var_Z;     //ref_Z = 108.883

	if((*X<7) && (*Y<4) && (*Z<1))
		cout<<L<<" "<<a<<" "<<b<<endl;

	if(*Z<0 || *Z>108.883)
	{
		cout<<L<<" "<<a<<" "<<b<<endl;
		//tst++;
	}
}

void convertXyzToRgb(float X,float Y,float Z, int *re,int  *gr,int *bl)
{
	float var_X, var_Y, var_Z, var_R, var_G, var_B;

	var_X = X / 100;        //X from 0 to  95.047   (Observer = 2? Illuminant = D65)
	var_Y = Y / 100;        //Y from 0 to 100.000
	var_Z = Z / 100;        //Z from 0 to 108.883

	var_R = var_X *  3.2406 + var_Y * -1.5372 + var_Z * -0.4986;
	var_G = var_X * -0.9689 + var_Y *  1.8758 + var_Z *  0.0415;
	var_B = var_X *  0.0557 + var_Y * -0.2040 + var_Z *  1.0570;

	if ( var_R > 0.0031308 )
		var_R = 1.055 * pow(var_R , ( 1 / 2.4 )) - 0.055;
	else
		var_R = 12.92 * var_R;

	if ( var_G > 0.0031308 )
		var_G = 1.055 * pow(var_G , ( 1 / 2.4 )) - 0.055;
	else
		var_G = 12.92 * var_G;

	if ( var_B > 0.0031308 )
		var_B = 1.055 * pow(var_B , ( 1 / 2.4 )) - 0.055;
	else
		var_B = 12.92 * var_B;

	*re = var_R * 255;
	*gr = var_G * 255;
	*bl = var_B * 255;

	if(abs(*re)>255 || *re<0) cout<< var_R<<" ";
	if(abs(*gr)>255 || *gr<0) cout<< var_G<<" ";

	if(*bl<0) nblue++;
	if(*gr<0) ngreen++;
	if(*re<0) nred++;

	//if(*bl<0 || *re<0 || *gr<0)
	//    cout<< var_B<<"**"<<X<<" "<<Y<<" "<<Z<<endl;

}
//lab color
void getColor(int m, double val, int *re, int *gr, int *bl)
{
	float amin[4], bmin[4], amax[4], bmax[4];

	float l, a, b, X, Y, Z, fact;

	amin[0] = 40;  bmin[0] = -8; //1st Col  Pink
	//amin[1] = 40;  bmin[1] = -8; //1st Col  Pink
	//amin[2] = 40;  bmin[2] = -8; //1st Col  Pink
	//amin[3] = 40;  bmin[3] = -8; //1st Col  Pink

	amin[1] = 17;  bmin[1] = -39;//2nd Col blue
	amin[2] = -40; bmin[2] = 8; //3rd Col  green
	amin[3] = 28;  bmin[3] = 30; //4th Col orange

	amax[0] = 6; bmax[0] = -1; //1st Col

	//amax[1] = 6; bmax[1] = -1; //1st Col
	//amax[2] = 6; bmax[2] = -1; //1st Col
	//amax[3] = 6; bmax[3] = -1; //1st Col

	amax[1] = 1; bmax[1] = -5; //2nd Col
	amax[2] = -5; bmax[2] = 1; //3rd Col
	amax[3] =  4; bmax[3] = 4; //4th Col

	//input value val is between 0 and 255
	fact = (255-val)/255.00;

	l= LMIN + fact *(LMAX-LMIN);
	switch(m)
	{
	case 0:
	{
		a = amin[0] + fact * (amax[0]-amin[0]);
		b = bmin[0] + fact * (bmax[0]-bmin[0]);  //interpolate for the first color. val(0:255)
		//if (a<0) cout<< fact<<" "<< amax[0]-amin[0]<< " "<< amin[0]<<endl;
		break;
	}
	case 1:
	{
		a = amin[1] + fact * (amax[1]-amin[1]);
		b = bmin[1] + fact * (bmax[1]-bmin[1]);
		//if (a<-100) cout<< fact<<" "<< amax[1]-amin[1]<< " "<< amin[1]<<endl;
		break;
	}
	case 2:
	{
		a = amin[2] + fact * (amax[2]-amin[2]);
		b = bmin[2] + fact * (bmax[2]-bmin[2]);
		//if (a<-100) cout<< fact<<" "<< amax[2]-amin[2]<< " "<< amin[2]<<endl;
		break;
	}
	case 3:
	{
		a = amin[3] + fact * (amax[3]-amin[3]);
		b = bmin[3] + fact * (bmax[3]-bmin[3]);
		//if (a<-100) cout<< fact<<" "<< amax[3]-amin[3]<< " "<< amin[3]<<endl;
		break;
	}
	}

	// The follwing old way of converting to RGB no longer work
	convertLabToXyz(l, a, b, &X, &Y, &Z);
	convertXyzToRgb(X, Y, Z, re, gr, bl);
}


/*
void getColor(int m, int val, int *re, int *gr, int *bl)
{
   float col1[10][3], col2[10][3], col3[10][3], col4[10][3];

   int ind;

   col1[0][0]=191; col2[0][0]=191; col3[0][0]=191; col4[0][0]=191;
   col1[0][1]=191; col2[0][1]=191; col3[0][1]=191; col4[0][1]=191;
   col1[0][2]=191; col2[0][2]=191; col3[0][2]=191; col4[0][2]=191;

   col1[1][0]=196; col2[1][0]=203; col3[1][0]= 179;col4[1][0]= 178; 
   col1[1][1]=180; col2[1][1]=203; col3[1][1]=190; col4[1][1]=181;
   col1[1][2]=177; col2[1][2]=159; col3[1][2]=182; col4[1][2]=195;

   col1[2][0]=202; col2[2][0]=208; col3[2][0]=165; col4[2][0]=159;
   col1[2][1]=265; col2[2][1]=208; col3[2][1]= 189;col4[2][1]=166;
   col1[2][2]=258; col2[2][2]=138; col3[2][2]=172; col4[2][2]=202;

   col1[3][0]=210; col2[3][0]=215; col3[3][0]=145; col4[3][0]=140;
   col1[3][1]=146; col2[3][1]=215; col3[3][1]=187; col4[3][1]=151;
   col1[3][2]=136; col2[3][2]=119; col3[3][2]=158; col4[3][2]=200;

   col1[4][0]=218; col2[4][0]=222; col3[4][0]=124; col4[4][0]=117;
   col1[4][1]=127; col2[4][1]=222; col3[4][1]=185; col4[4][1]=132;
   col1[4][2]=111; col2[4][2]=99; col3[4][2]=143; col4[4][2]=217;

   col1[5][0]=227; col2[5][0]=229; col3[5][0]=104; col4[5][0]=90;
   col1[5][1]=105; col2[5][1]=229; col3[5][1]=184; col4[5][1]=111;
   col1[5][2]=82;  col2[5][2]=78;  col3[5][2]=127; col4[5][2]=227;

   col1[6][0]=236; col2[6][0]=235; col3[6][0]=82;  col4[6][0]=64; 
   col1[6][1]=85;  col2[6][1]=235;  col3[6][1]=181; col4[6][1]=92;
   col1[6][2]=57;  col2[6][2]=59; col3[6][2]=112; col4[6][2]=235;

   col1[7][0]=243; col2[7][0]=242; col3[7][0]= 63; col4[7][0]= 42;
   col1[7][1]=67;  col2[7][1]=242;  col3[7][1]=179; col4[7][1]= 74;
   col1[7][2]=34;  col2[7][2]=39; col3[7][2]=98;  col4[7][2]= 243;

   col1[8][0]=250; col2[8][0]=248; col3[8][0]=47;  col4[8][0]=24; 
   col1[8][1]=50;  col2[8][1]=248;  col3[8][1]=178; col4[8][1]=60;
   col1[8][2]=14;  col2[8][2]=21; col3[8][2]=87;  col4[8][2]=250;

   col1[9][0]=255; col2[9][0]=255; col3[9][0]=35;  col4[9][0]=11; 
   col1[9][1]=39;  col2[9][1]=255;   col3[9][1]=178; col4[9][1]=49;
   col1[9][2]=0;   col2[9][2]=0; col3[9][2]=78;  col4[9][2]=255;
 */
/*
   col1[0][0]=191; col2[0][0]=191; col3[0][0]=191; col4[0][0]=191;
   col1[0][1]=191; col2[0][1]=191; col3[0][1]=191; col4[0][1]=191;
   col1[0][2]=191; col2[0][2]=191; col3[0][2]=191; col4[0][2]=191;

   col1[1][0]=196; col2[1][0]=191; col3[1][0]= 179;col4[1][0]= 178; 
   col1[1][1]=180; col2[1][1]=178; col3[1][1]=190; col4[1][1]=181;
   col1[1][2]=177; col2[1][2]=191; col3[1][2]=182; col4[1][2]=195;

   col1[2][0]=202; col2[2][0]=193; col3[2][0]=165; col4[2][0]=159;
   col1[2][1]=265; col2[2][1]=158; col3[2][1]= 189;col4[2][1]=166;
   col1[2][2]=258; col2[2][2]=191; col3[2][2]=172; col4[2][2]=202;

   col1[3][0]=210; col2[3][0]=194; col3[3][0]=145; col4[3][0]=140;
   col1[3][1]=146; col2[3][1]=136; col3[3][1]=187; col4[3][1]=151;
   col1[3][2]=136; col2[3][2]=191; col3[3][2]=158; col4[3][2]=200;

   col1[4][0]=218; col2[4][0]=195; col3[4][0]=124; col4[4][0]=117;
   col1[4][1]=127; col2[4][1]=112; col3[4][1]=185; col4[4][1]=132;
   col1[4][2]=111; col2[4][2]=190; col3[4][2]=143; col4[4][2]=217;

   col1[5][0]=227; col2[5][0]=197; col3[5][0]=104; col4[5][0]=90;
   col1[5][1]=105; col2[5][1]=86;  col3[5][1]=184; col4[5][1]=111;
   col1[5][2]=82;  col2[5][2]=190; col3[5][2]=127; col4[5][2]=227;

   col1[6][0]=236; col2[6][0]=199; col3[6][0]=82;  col4[6][0]=64; 
   col1[6][1]=85;  col2[6][1]=60;  col3[6][1]=181; col4[6][1]=92;
   col1[6][2]=57;  col2[6][2]=191; col3[6][2]=112; col4[6][2]=235;

   col1[7][0]=243; col2[7][0]=200; col3[7][0]= 63; col4[7][0]= 42;
   col1[7][1]=67;  col2[7][1]=37;  col3[7][1]=179; col4[7][1]= 74;
   col1[7][2]=34;  col2[7][2]=191; col3[7][2]=98;  col4[7][2]= 243;

   col1[8][0]=250; col2[8][0]=201; col3[8][0]=47;  col4[8][0]=24; 
   col1[8][1]=50;  col2[8][1]=18;  col3[8][1]=178; col4[8][1]=60;
   col1[8][2]=14;  col2[8][2]=191; col3[8][2]=87;  col4[8][2]=250;

   col1[9][0]=255; col2[9][0]=202; col3[9][0]=35;  col4[9][0]=11; 
   col1[9][1]=39;  col2[9][1]=5;   col3[9][1]=178; col4[9][1]=49;
   col1[9][2]=0;   col2[9][2]=190; col3[9][2]=78;  col4[9][2]=255;

   ind = val-10;

                   //pick 0 to 9 bin


    switch(m) {

    case 0: { *re=col1[ind][0]; *gr=col1[ind][1]; *bl= col1[ind][2]; //interpolate for the first color. val(0:255)
              break;}
    case 1: { *re=col2[ind][0]; *gr=col2[ind][1]; *bl= col2[ind][2];
        break;}
    case 2: { *re=col3[ind][0]; *gr=col3[ind][1]; *bl= col3[ind][2];
        break;}
    case 3: { *re=col4[ind][0]; *gr=col4[ind][1]; *bl= col4[ind][2];
        break;}
    } 
}

{
    double L, a, b;
    double X, Y, Z;
    double R, G, B;

    // Lab -> normalized XYZ (X,Y,Z are all in 0...1)

    Y = L * (1.0/116.0) + 16.0/116.0;
    X = a * (1.0/500.0) + Y;
    Z = b * (-1.0/200.0) + Y;

    X = X > 6.0/29.0 ? X * X * X : X * (108.0/841.0) - 432.0/24389.0;
    Y = L > 8.0 ? Y * Y * Y : L * (27.0/24389.0);
    Z = Z > 6.0/29.0 ? Z * Z * Z : Z * (108.0/841.0) - 432.0/24389.0;

    // normalized XYZ -> linear sRGB (in 0...1)

    R = X * (1219569.0/395920.0)     + Y * (-608687.0/395920.0)    + Z * (-107481.0/197960.0);
    G = X * (-80960619.0/87888100.0) + Y * (82435961.0/43944050.0) + Z * (3976797.0/87888100.0);
    B = X * (93813.0/1774030.0)      + Y * (-180961.0/887015.0)    + Z * (107481.0/93370.0);

    // linear sRGB -> gamma-compressed sRGB (in 0...1)

    R = R > 0.0031308 ? pow(R, 1.0 / 2.4) * 1.055 - 0.055 : R * 12.92;
    G = G > 0.0031308 ? pow(G, 1.0 / 2.4) * 1.055 - 0.055 : G * 12.92;
    B = B > 0.0031308 ? pow(B, 1.0 / 2.4) * 1.055 - 0.055 : B * 12.92;
}
 */

// helper functions
double setArr(bool isValid, double val)
{
	if(isValid)
	{
		return val;
	}
	else
	{
		return 0;
	}
}



int main(int argc, char* argv[])
{
	char line[256];
	char dummy[80];
	char in_name[4][80];
	char out_name[80] =" ";
	int i, j, k, l, cols, wcol;

	int n_rows = 61;
	int n_cols = 122;
	double xmax = 1;
	float grd_sz, xmin, ymin, ymax, nm, elem, avg=0, minE, maxE;
	int red, green, blue;

	double  val[4], **arr, **colArr; //arr[SCL*2][725*SCL*2];

	//Read in: cpre6190_o ctmn6190_o cvap6190_o cwnd6190_o
	cout << "start!" << endl;
	for (i=0; i<argc-1; i++)
		{
			strcpy(in_name[i],  argv[i+1]);
			strcat(in_name[i], ".pgm");
			cout<<"Opening the file name "<<in_name[i]<<endl;
		}

	string out = argv[1];
	out = out.substr(5, 3);
	//strcpy(out_name, out.c_str());
	sprintf(out_name, "%s.ppm", out.c_str());
	ifstream inf0(in_name[0]), inf1(in_name[1]), inf2(in_name[2]), inf3(in_name[3]);
	ofstream outf(out_name);

	//get rid of the first 3 lines
	inf0>> dummy; //read header P2
	cout<< dummy << endl;
	inf1>> dummy; //read header P2
	inf2>> dummy; //read header P2
	inf3>> dummy; //read header P2

	inf0>> n_cols>> n_rows;
	cout<< n_cols<< " "<<n_rows<< " "<<endl;

	inf1>> n_cols>> n_rows;
	cout<< n_cols<< " "<<n_rows<<endl;

	inf2>> n_cols>> n_rows;
	cout<< n_cols<< " "<<n_rows <<endl;

	inf3>> n_cols>> n_rows;
	cout<< n_cols<< " "<<n_rows<< " "<<endl;

	inf0>> xmax; //read 255
	inf1>> xmax; //read 255
	inf2>> xmax; //read 255
	inf3>> xmax; //read 255

	cout<<"xmax: " << xmax<<endl;

	// Write into an array
	outf<<"P3"<<endl;
	xmin = n_rows*SCL*2; xmax = n_cols*SCL*2; //357*10  357*10

	outf<<xmax <<" "<< xmin<<endl;
	cout<< n_cols<<" "<<SCL*2<<" "<<xmax<<endl;
	outf<<"255"<<endl;

	int cnt=0, tmp=0;
	int size1 = BCL*n_rows;  // 610
	int size2 = BCL*n_cols; // 1220
	arr = (double **) malloc(size1*sizeof(double));
	for(i=0;i< size1;i++)
	{
		arr[i] = (double*)malloc(size2*sizeof(double));
	}
	colArr = (double**) malloc(size1*sizeof(double));
	for(i=0;i< size1;i++)
	{
		colArr[i] = (double *) malloc(size2*sizeof(double));
	}

	srand((unsigned)time(0));
	bool isValid;

	for (int r = 0; r < n_rows; r++)
	{
		int wrow = r*BCL;
		for(int c=0; c < n_cols; c++)
		{
			inf0>>val[0];
			inf1>>val[1];
			inf2>>val[2];
			inf3>>val[3];

			//if(c%2 != 0) continue;    // ******

			int myRand[4], ind=0, rint;

			myRand[0]=0;
			myRand[1]=1;
			myRand[2]=2;
			myRand[3]=3;
			wcol = c*BCL;

			// if in one region, one of the four values is not valid (i.e. -9999), set current region not valid
			if((val[myRand[0]] == 0) || (val[myRand[1]] == 0) || (val[myRand[2]] == 0) || (val[myRand[3]] == 0))
			{
				isValid = false;
			}
			else
			{
				isValid = true;
			}

			for (int k=0; k<4; k++)
			{
				switch(myRand[k])
				{
				// region 0: upper left corner
				case 0:
				{
					for (i=wrow; i < wrow + SCL; i++)
					{
						for(j=wcol; j<(wcol + SCL); j++)
						{
							arr[i][j] = setArr(isValid, val[myRand[0]]);
							colArr[i][j] = myRand[0];

						}
					}
					break;
				}
				// region 1: upper right corner
				case 1:
				{
					for (i = wrow; i < wrow + SCL; i++)
					{
						for(j=(wcol + SCL); j<(wcol + BCL); j++)
						{
							arr[i][j] = setArr(isValid, val[myRand[1]]);
							colArr[i][j] = myRand[1];
						}
					}
					break;
				}
				// region 2: lower left corner
				case 2:
				{
					for(i=wrow + SCL; i<(wrow + BCL); i++)
					{
						for(j=wcol; j<(wcol+SCL); j++)
						{
							arr[i][j] = setArr(isValid, val[myRand[2]]);
							colArr[i][j] = myRand[2];
						}
					}
					break;
				}
				// region 3: lower right corner
				case 3:
				{
					for (i=wrow + SCL; i<(wrow + BCL); i++)
					{
						for(j=(wcol + SCL); j<(wcol + BCL); j++)
						{
							arr[i][j] = setArr(isValid, val[myRand[3]]);
							colArr[i][j] = myRand[3];
						}
					}
					break;
				}
				}
			}//for cols-> loop
		}

		//skip one row;
		//		for(cols=0; cols<n_cols; cols++)
		//		{
		//			inf0>>val[0];
		//			inf1>>val[1];
		//			inf2>>val[2];
		//			inf3>>val[3];
		//		}

	}
	cout << "writing to " << out_name << endl;

	// write all data (in arr[i][j] for all i and j) to output file
	for(i=0; i < size1; i++)
	{
		//for(j=0;j<2*BCL*n_cols; j++)
		for(j=0;j < size2; j++)
		{
			// if the data is not valid, output color be grey (i.e. (r,g,b)=(125,125,125))
			if(arr[i][j] == 0)
			{
				outf<<125 <<" "<<125 <<" "<<125 <<" ";
			}
			else
			{
				getColor(colArr[i][j], arr[i][j], &red, &green, &blue);
				//getColor(3, arr[i][j], &red, &green, &blue);
				outf<<red<<" "<<green<<" "<<blue<<" ";
			}
		}
		outf << endl;
	}
	cout << "done" << endl;

	//cleanup!
	delete [] arr;
	arr=NULL;
	outf.close();
	// Then write to a file
} 

