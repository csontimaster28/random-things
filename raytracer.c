#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <jpeglib.h>

#define WIDTH 800
#define HEIGHT 600
#define MAX_DEPTH 3

// ---------------- VECTOR ----------------

typedef struct { double x,y,z; } Vec3;

Vec3 v(double x,double y,double z){ return (Vec3){x,y,z}; }
Vec3 add(Vec3 a,Vec3 b){ return v(a.x+b.x,a.y+b.y,a.z+b.z); }
Vec3 sub(Vec3 a,Vec3 b){ return v(a.x-b.x,a.y-b.y,a.z-b.z); }
Vec3 mul(Vec3 a,double k){ return v(a.x*k,a.y*k,a.z*k); }
double dot(Vec3 a,Vec3 b){ return a.x*b.x+a.y*b.y+a.z*b.z; }
Vec3 norm(Vec3 a){
    double l=sqrt(dot(a,a));
    return l>0?mul(a,1.0/l):a;
}
Vec3 reflect(Vec3 I,Vec3 N){
    return sub(I,mul(N,2*dot(I,N)));
}

// ---------------- OBJECTS ----------------

typedef struct {
    Vec3 center;
    double radius;
    Vec3 color;
    double refl;
} Sphere;

typedef struct {
    Vec3 point;
    Vec3 normal;
} Plane;

// ---------------- SCENE ----------------

Sphere spheres[] = {
    { {0,1,-6}, 1, {1,0,0}, 0.5 },
    { {2,1,-7}, 1, {0,1,0}, 0.3 },
    { {-2,1,-7},1, {0,0,1}, 0.8 }
};

Plane floor_plane = { {0,0,0}, {0,1,0} };
Vec3 light = {5,8,-3};
Vec3 camera = {0,1,2};

// ---------------- INTERSECTIONS ----------------

double intersect_sphere(Vec3 ro,Vec3 rd,Sphere*s){
    Vec3 oc=sub(ro,s->center);
    double b=dot(oc,rd);
    double c=dot(oc,oc)-s->radius*s->radius;
    double h=b*b-c;
    if(h<0) return -1;
    return -b-sqrt(h);
}

double intersect_plane(Vec3 ro,Vec3 rd,Plane*p){
    double d=dot(p->normal,rd);
    if(fabs(d)<1e-6) return -1;
    double t=dot(sub(p->point,ro),p->normal)/d;
    return t>0?t:-1;
}

// ---------------- TRACE ----------------

Vec3 trace(Vec3 ro,Vec3 rd,int depth){
    double tmin=1e9;
    Sphere* hit=NULL;
    int hit_plane=0;

    for(int i=0;i<3;i++){
        double t=intersect_sphere(ro,rd,&spheres[i]);
        if(t>0 && t<tmin){ tmin=t; hit=&spheres[i]; hit_plane=0; }
    }

    double tp=intersect_plane(ro,rd,&floor_plane);
    if(tp>0 && tp<tmin){ tmin=tp; hit_plane=1; }

    if(tmin==1e9) return v(0.1,0.1,0.15); // háttér

    Vec3 hitp=add(ro,mul(rd,tmin));
    Vec3 N;
    Vec3 base_color;

    if(hit_plane){
        N=floor_plane.normal;
        int check=((int)floor(hitp.x)+(int)floor(hitp.z))&1;
        base_color=check?v(1,1,1):v(0,0,0);
    }else{
        N=norm(sub(hitp,hit->center));
        base_color=hit->color;
    }

    Vec3 L=norm(sub(light,hitp));
    double diff=fmax(0,dot(N,L));

    // shadow
    double shadow=1.0;
    for(int i=0;i<3;i++){
        double ts=intersect_sphere(add(hitp,mul(N,0.01)),L,&spheres[i]);
        if(ts>0){ shadow=0.2; break; }
    }

    Vec3 col=mul(base_color,diff*shadow);

    // reflection
    if(!hit_plane && hit->refl>0 && depth<MAX_DEPTH){
        Vec3 R=reflect(rd,N);
        Vec3 rc=trace(add(hitp,mul(N,0.01)),R,depth+1);
        col=add(mul(col,1-hit->refl),mul(rc,hit->refl));
    }

    return col;
}

// ---------------- JPG SAVE ----------------

void save_jpg(unsigned char*img){
    struct jpeg_compress_struct cinfo;
    struct jpeg_error_mgr jerr;

    FILE* f=fopen("render.jpg","wb");
    cinfo.err=jpeg_std_error(&jerr);
    jpeg_create_compress(&cinfo);
    jpeg_stdio_dest(&cinfo,f);

    cinfo.image_width=WIDTH;
    cinfo.image_height=HEIGHT;
    cinfo.input_components=3;
    cinfo.in_color_space=JCS_RGB;

    jpeg_set_defaults(&cinfo);
    jpeg_set_quality(&cinfo,95,TRUE);
    jpeg_start_compress(&cinfo,TRUE);

    JSAMPROW row;
    while(cinfo.next_scanline<cinfo.image_height){
        row=&img[cinfo.next_scanline*WIDTH*3];
        jpeg_write_scanlines(&cinfo,&row,1);
    }

    jpeg_finish_compress(&cinfo);
    fclose(f);
    jpeg_destroy_compress(&cinfo);
}

// ---------------- MAIN ----------------

int main(){
    unsigned char*img=malloc(WIDTH*HEIGHT*3);

    for(int y=0;y<HEIGHT;y++){
        for(int x=0;x<WIDTH;x++){
            double px = (2*(x+0.5)/WIDTH - 1) * (double)WIDTH / HEIGHT;
            double py = 1 - 2*(y+0.5)/HEIGHT;
            
            Vec3 rd = norm(v(px, py, -1));
            Vec3 c=trace(camera,rd,0);

            int i=(y*WIDTH+x)*3;
            img[i]=(unsigned char)(pow(c.x,1/2.2)*255);
            img[i+1]=(unsigned char)(pow(c.y,1/2.2)*255);
            img[i+2]=(unsigned char)(pow(c.z,1/2.2)*255);
        }
    }

    save_jpg(img);
    free(img);
    printf("Kész: render.jpg\n");
}
