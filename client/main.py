from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDRectangleFlatButton
import requests
import threading
from kivy.metrics import dp
from kivymd.uix.datatables import MDDataTable
import kivy.clock
import wikipediaapi
from PIL import Image

class MainWid(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__()
        self.startwid = StartWid(self)
        self.editwid = EditWid(self)
        self.datawid = DataWid(self)

        wid = Screen(name = 'Start')
        wid.add_widget(self.startwid)
        self.add_widget(wid)
    
        wid = Screen(name='Edit')
        wid.add_widget(self.editwid)
        self.add_widget(wid)

        wid = Screen(name='Data')
        wid.add_widget(self.datawid)
        self.add_widget(wid)
        self.goto_start()
 
    def goto_start(self, *args):
        self.current = 'Start'

    def goto_table(self, *args):
        self.current = 'Edit'

    def goto_data(self, *args):
        self.current = 'Data'

    def clear_screen(self, *args):
        self.editwid.clear_widgets()


class StartWid(FloatLayout):
    def __init__(self, mainwid, **kwargs):
        super().__init__()
        self.mainwid = mainwid

    def capture(self, *args):
        camera = self.ids["camera"]
        camera.export_to_png("/storage/emulated/0/oscar.png")

#        camera.export_to_png("oscar.png")

        img = Image.open("/storage/emulated/0/oscar.png")

#        img = Image.open("oscar.png")
        dimension=(375, 500)

        resized = img.resize(dimension)
        resized.save("/storage/emulated/0/resized.png")
#        resized.save("resized.png")

    def goto_predict(self):
        self.mainwid.editwid.update()
        self.mainwid.goto_table()
        self.capture()

    def close_cam(self):
        cam = self.ids["camera"]
        cam.play = False

    def thread_gen(self, *args):
        threading.Thread(target=self.predictions, args=(args,)).start()

    def predictions(self, *args):
        self.mainwid.editwid.predict()
        self.mainwid.editwid.createtable()


class EditWid(FloatLayout):
    def __init__(self, mainwid, **kwargs):
        super().__init__()
        self.mainwid = mainwid

    def update(self, *args):
        spin = MDSpinner(
            id = "spin",
            size_hint = (None, None),
            size = (dp(46), dp(46)),
            pos_hint = {'center_x':0.5, 'center_y':0.5},
            active = True
        )
        self.add_widget(spin)

    def predict(self, *args):
        KERAS_REST_API_URL = "http://www.terah.online/predict"
#        IMAGE_PATH = "resized.png"

        IMAGE_PATH = "/storage/emulated/0/resized.png"
        
        image = open(IMAGE_PATH, "rb").read()
        payload = {"image": image}
        r = requests.post(KERAS_REST_API_URL, files=payload).json()
        if r["success"]:
            data = [(result["label"], format(result["probability"], '.2f')) for result in r["predictions"]]

        else:
            print("unknown error")


        return data

    @kivy.clock.mainthread
    def createtable(self, *args):
        data = self.predict()
        table = MDDataTable(pos_hint={"center_x":0.5, "center_y":0.5},
                size_hint = (0.9, 0.6),
                check=True,
                rows_num=10,
                column_data=[
            ("Label", dp(30)),
            ("Prediction", dp(30))
            ],

            row_data=[
                k for k in data
                ] )
        table.bind(on_check_press=self.check_press)

        btn = MDRectangleFlatButton(
                text = "Back",
                pos = (0, 0),
                size_hint = (1.0, 0.1)
            )
        btn.bind(on_release=self.mainwid.goto_start)
        btn.bind(on_release=self.mainwid.clear_screen)

        self.add_widget(table)
        self.add_widget(btn)

    def check_press(self, instance_table, current_row):
        self.mainwid.goto_data()
        self.mainwid.datawid.backs()
        self.checks(instance_table, current_row)

    def checks(self, instance_table, current_row):
        terah = str(current_row[0])
        
        wiki_wiki = wikipediaapi.Wikipedia('en')
        page_py = wiki_wiki.page(terah)

        labs = self.mainwid.datawid.ids.labs
        labs.text = page_py.summary[0:400]

#        except:
#            labs = self.mainwid.datawid.ids.labs
#            labs.text = "{} has many variations".format(terah)
  
   

class DataWid(FloatLayout):
    def __init__(self, mainwid, **kwargs):
        super().__init__()
        self.mainwid = mainwid

    def clear_data(self, *args):
        labs = self.ids.labs
        labs.text = ""

    def backs(self):
        btn = MDRectangleFlatButton(
                text = "Back",
                pos = (0, 0),
                size_hint = (1.0, 0.1)
            )
        btn.bind(on_release=self.mainwid.goto_table)
        btn.bind(on_release=self.clear_data)
        self.add_widget(btn)

class MainApp(MDApp):
    def build(self):
        return MainWid()


if __name__=='__main__':
    MainApp().run()
