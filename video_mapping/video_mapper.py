import numpy as np
import cv2

def while_p():
    x = 0
    while(True):
        x += 1
        yield x

class VideoMapper:
    def __init__(self):#
        # capture frames from a camera

        self.cap = cv2.VideoCapture(0)

        self.resolution = (int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),3)
        self.buffer_size = 1000
        self.frame_buffer = np.zeros((self.buffer_size, *self.resolution))
        self.frame_step = 0
        self.cap.read()

        self.image = np.zeros(self.resolution, dtype=np.uint8)

        self.color_interval = 160
        self.lower = np.array([30, 50, 50])
        self.upper = np.array([255, 255, 180])


        self.edge_buffer = np.zeros((self.buffer_size,*self.resolution))
        #self.start()
        #self.exit()

    def start(self):
        for i in while_p():
            self.step_i = i
            status = self.step()
            if i > 1000 or not status:
                break



    def add_frame_to_buffer(self, frame):
        assert(np.shape(frame) == self.resolution , np.shape(frame) )
        self.frame_buffer[self.frame_step%self.buffer_size] = frame
        self.frame_step += 1

    def step(self):


        # reads frames from a camera
        ret, frame = self.cap.read()
        if not ret:
            print("There is no Frame right now :/ ", ret)
            return
        self.add_frame_to_buffer(frame)

        # converting BGR to HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        if(self.step_i%self.color_interval ==0):
            # define range of red color in HSV
            self.lower, self.upper = np.sort(np.random.randint(0, 255, size=(2, 3)), axis=0)
            print("Changed range to", self.lower, self.upper)


        if np.random.rand() > 0.5:
            expand_dim = np.random.randint(0,3)
            self.lower[expand_dim] = np.clip(self.lower[expand_dim] - 2, 0, 255)
        else:
            expand_dim = np.random.randint(0, 3)
            self.upper[expand_dim] = np.clip(self.upper[expand_dim] + 2, 0, 255)

        # create a red HSV colour boundary and
        # threshold HSV image
        mask = cv2.inRange(hsv, self.lower, self.upper)
        mask_3d = np.dstack([mask]*3)
        # Bitwise-AND mask and original image
        res = cv2.bitwise_and(frame, mask_3d)

        # Display an original image
        #cv2.imshow('Original', frame)
        #cv2.imshow('Original', res)
        # finds edges in the input image image and
        # marks them in the output map edges
        edges = cv2.Canny(frame, 100, 200)

        self.edge_buffer[self.step_i % self.buffer_size] = edges[..., None]

        mean_edge = self.get_edges("often", n_past=20)

        #combined = np.clip( mean_edge + res, 0, 255)
        combined = mean_edge
        self.image = np.asarray(0.4 * combined + 0.6 * self.image, dtype= np.uint8)

        areas = self.get_areas(mean_edge)
        print(np.mean(areas))
        inverse_areas = np.asarray(255 - areas, dtype=np.uint8)
        print("Area Shape", np.shape(areas), np.shape(frame), np.shape(self.image), np.shape(inverse_areas))
        print("Types:", areas.dtype, frame.dtype, self.image.dtype, inverse_areas.dtype)
        edges_area = cv2.bitwise_and(areas, self.image)
        real_area = cv2.bitwise_and(inverse_areas, frame)

        print(np.shape(real_area),np.shape(edges_area))
        self.image = cv2.bitwise_or(real_area , edges_area)

        # Display in a frame
        cv2.imshow('Edges', self.image)

        # Wait for Esc key to stop
        k = cv2.waitKey(5) & 0xFF
        if k == 27:
            return False

        return True

    def get_edges(self, mode = "mean", n_past=10):

        rolling_index = (-1 * np.arange(n_past) + self.step_i % self.buffer_size) % self.buffer_size
        if mode == "mean":
            return np.mean(self.edge_buffer[rolling_index], axis=0)
        if mode == "median":
            #Makes moving objects invisible
            return np.median(self.edge_buffer[rolling_index], axis=0)
        if mode == "often":
            return (np.sum(self.edge_buffer[rolling_index], axis=0) > 128 * n_past) * 255

    def get_areas(self, edges):
        #TODO Cluster edges rowwise, fill every 2nd cluster

        assert(len(np.shape(edges)) == 3)
        h,w,d = np.shape(edges)
        areas = np.zeros((h,w,d), dtype=np.uint8)
        for i in range(h):
            running = 0
            for j in range(w):
                if edges[i,j-1,0] > 0 and edges[i,j,0] == 0:
                    running += 1
                if edges[i,j,0] > 0:
                    areas[i, j, :] = 1

                else:
                    areas[i, j, :] = (running % 2)*255


        return areas

    def exit(self):
        # Close the window
        self.cap.release()

        # De-allocate any associated memory usage
        cv2.destroyAllWindows()

def main():
    VM = VideoMapper()
    VM.start()
    VM.exit()


if __name__ == "__main__":
    main()