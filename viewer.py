from OpenGL.GL import glCallList, glClear, glClearColor, glColorMaterial, glCullFace, glDepthFunc, glDisable, glEnable,\
                      glFlush, glGetFloatv, glLightfv, glLoadIdentity, glMatrixMode, glMultMatrixf, glPopMatrix, \
                      glPushMatrix, glTranslated, glViewport, \
                      GL_AMBIENT_AND_DIFFUSE, GL_BACK, GL_CULL_FACE, GL_COLOR_BUFFER_BIT, GL_COLOR_MATERIAL, \
                      GL_DEPTH_BUFFER_BIT, GL_DEPTH_TEST, GL_FRONT_AND_BACK, GL_LESS, GL_LIGHT0, GL_LIGHTING, \
                      GL_MODELVIEW, GL_MODELVIEW_MATRIX, GL_POSITION, GL_PROJECTION, GL_SPOT_DIRECTION
from OpenGL.constants import GLfloat_3, GLfloat_4
from OpenGL.GLU import gluPerspective, gluUnProject
from OpenGL.GLUT import glutCreateWindow, glutDisplayFunc, glutGet, glutInit, glutInitDisplayMode, \
                        glutInitWindowSize, glutMainLoop, \
                        GLUT_SINGLE, GLUT_RGB, GLUT_WINDOW_HEIGHT, GLUT_WINDOW_WIDTH, glutCloseFunc
import numpy
from numpy.linalg import norm, inv
import random
from OpenGL.GL import glBegin, glColor3f, glEnd, glEndList, glLineWidth, glNewList, glNormal3f, glVertex3f, \
                      GL_COMPILE, GL_LINES, GL_QUADS
from OpenGL.GLU import gluDeleteQuadric, gluNewQuadric, gluSphere

import color
from scene import Scene
from primitive import init_primitives, G_OBJ_PLANE
from node import Sphere, Cube, SnowFigure
from interaction import Interaction



class Viewer(object):
    def __init__(self):
        """ Initialize the viewer. """
        #初始化接口，创建窗口并注册渲染函数
        self.init_interface()
        #初始化opengl的配置
        self.init_opengl()
        #初始化3d场景
        self.init_scene()
        #初始化交互操作相关的代码
        self.init_interaction()
        init_primitives()

    def init_interface(self):
        """ 初始化窗口并注册渲染函数 """
        glutInit()
        glutInitWindowSize(640, 480)
        glutCreateWindow(b"3D Modeller")
        glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
        #注册窗口渲染函数
        glutDisplayFunc(self.render)

    def init_opengl(self):
        """ 初始化opengl的配置 """
        #模型视图矩阵
        self.inverseModelView = numpy.identity(4)
        #模型视图矩阵的逆矩阵
        self.modelView = numpy.identity(4)

        #开启剔除操作效果
        glEnable(GL_CULL_FACE)
        #取消对多边形背面进行渲染的计算（看不到的部分不渲染）
        glCullFace(GL_BACK)
        #开启深度测试
        glEnable(GL_DEPTH_TEST)
        #测试是否被遮挡，被遮挡的物体不予渲染
        glDepthFunc(GL_LESS)
        #启用0号光源
        glEnable(GL_LIGHT0)
        #设置光源的位置
        glLightfv(GL_LIGHT0, GL_POSITION, GLfloat_4(0, 0, 1, 0))
        #设置光源的照射方向
        glLightfv(GL_LIGHT0, GL_SPOT_DIRECTION, GLfloat_3(0, 0, -1))
        #设置材质颜色
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glEnable(GL_COLOR_MATERIAL)
        #设置清屏的颜色
        glClearColor(0.4, 0.4, 0.4, 0.0)

    def init_scene(self):
        #创建一个场景实例
        self.scene = Scene()
        #初始化场景内的对象
        self.create_sample_scene()

    def create_sample_scene(self):
        cube_node = Cube()
        cube_node.translate(2, 0, 2)
        cube_node.color_index = 1
        self.scene.add_node(cube_node)

        sphere_node = Sphere()
        sphere_node.translate(-2, 0, 2)
        sphere_node.color_index = 3
        self.scene.add_node(sphere_node)

        hierarchical_node = SnowFigure()
        hierarchical_node.translate(-2, 0, -2)
        self.scene.add_node(hierarchical_node)

    def init_interaction(self):
        self.interaction = Interaction()
        self.interaction.register_callback('pick', self.pick)
        self.interaction.register_callback('move', self.move)
        self.interaction.register_callback('place', self.place)
        self.interaction.register_callback('rotate_color', self.rotate_color)
        self.interaction.register_callback('scale', self.scale)

    def get_ray(self, x, y):
        self.init_view()

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # 得到激光的起始点
        start = numpy.array(gluUnProject(x, y, 0.001))
        end = numpy.array(gluUnProject(x, y, 0.999))

        # 得到激光的方向
        direction = end - start
        direction = direction / norm(direction)

        return (start, direction)



    def pick(self, x, y):
        """ 是否被选中以及哪一个被选中交由Scene下的pick处理 """
        start, direction = self.get_ray(x, y)
        self.scene.pick(start, direction, self.modelView)



    def move(self, x, y):
        """ 移动当前选中的节点 """
        start, direction = self.get_ray(x, y)
        self.scene.move_selected(start, direction, self.inverseModelView)



    def place(self, shape, x, y):
        """ 在鼠标的位置上新放置一个节点 """
        start, direction = self.get_ray(x, y)
        self.scene.place(shape, start, direction, self.inverseModelView)



    def rotate_color(self, forward):
        """ 更改选中节点的颜色 """
        #start, direction = self.get_ray(x, y)
        #self.scene.rotate_color(start,direction,self.inverseModelView)
        pass

    def scale(self, up):
        """ 改变选中节点的大小 """
        pass

    def main_loop(self):
        #程序主循环开始
        glutMainLoop()

    def render(self):
        #初始化投影矩阵
        self.init_view()

        #启动光照
        glEnable(GL_LIGHTING)
        #清空颜色缓存与深度缓存
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        #设置模型视图矩阵，这节课先用单位矩阵就行了。
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glMultMatrixf(self.interaction.trackball.matrix)

        # 存储ModelView矩阵与其逆矩阵之后做坐标系转换用
        currentModelView = numpy.array(glGetFloatv(GL_MODELVIEW_MATRIX))
        self.modelView = numpy.transpose(currentModelView)
        self.inverseModelView = inv(numpy.transpose(currentModelView))


        #渲染场景
        self.scene.render()

        #每次渲染后复位光照状态
        glDisable(GL_LIGHTING)
        glCallList(G_OBJ_PLANE)
        glPopMatrix()
        #把数据刷新到显存上
        glFlush()

    def init_view(self):
        """ 初始化投影矩阵 """
        xSize, ySize = glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT)
        #得到屏幕宽高比
        aspect_ratio = float(xSize) / float(ySize)

        #设置投影矩阵
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        #设置视口，应与窗口重合
        glViewport(0, 0, xSize, ySize)
        #设置透视，摄像机上下视野幅度70度
        #视野范围到距离摄像机1000个单位为止。
        gluPerspective(70, aspect_ratio, 0.1, 1000.0)
        #摄像机镜头从原点后退15个单位
        glTranslated(0, 0, -15)



if __name__ == "__main__":
    viewer = Viewer()
    viewer.main_loop()

