from datetime import datetime
import pprint
import copy

from feature_extractor import *


class Block_Controller(object):
    # GetNextMove is main function.
    # input
    #    GameStatus : this data include all field status,
    #                 in detail see the internal GameStatus data.
    # output
    #    nextMove : this data include next shape position and the other,
    #               if return None, do nothing to nextMove.
    def GetNextMove(self, nextMove, GameStatus, BOARD_DATA):

        t1 = datetime.now()

        # print GameStatus
        print("=================================================>")
        pprint.pprint(GameStatus, width = 61, compact = True)

        #  #                   ##             ##
        # ### -> (0, 1, 2, 3)   ## -> (0, 1)  ## -> (0)
        CurrentShapeDirectionRange = GameStatus["block_info"]["currentShape"]["direction_range"]
        # Shape() クラス
        self.CurrentShape_class = GameStatus["block_info"]["currentShape"]["class"]
        NextShapeDirectionRange = GameStatus["block_info"]["nextShape"]["direction_range"]
        self.NextShape_class = GameStatus["block_info"]["nextShape"]["class"]
        # 0
        self.ShapeNone_index = GameStatus["debug_info"]["shape_info"]["shapeNone"]["index"]
        # 9列のBOARD_DATA
        self.BOARD_DATA = copy.deepcopy(BOARD_DATA)
        backBoard2d = get_backBoard2d(self.BOARD_DATA)
        backBoard2d_9cols = backBoard2d[:, :-1]
        self.BOARD_DATA.backBoard = get_backBoard1d(backBoard2d_9cols)
        self.BOARD_DATA.width -= 1

        if self.CurrentShape_class.shape == 1 and whether_can_put_I_in(self.BOARD_DATA):
            strategy = (0, BOARD_DATA.width, 1, 1)
        else:
            LatestEvalValue = -100000
            strategy = (0, 5, 1, 1)
            for direction0 in CurrentShapeDirectionRange:
                x0Min, x0Max = self.getSearchXRange(self.CurrentShape_class, direction0)
                for x0 in range(x0Min, x0Max):
                    self.BOARD_DATA_tmp = self.getBoard(self.BOARD_DATA, self.CurrentShape_class, direction0, x0)
                    # print(get_backBoard2d(self.BOARD_DATA_tmp))

                    EvalValue = self.calcEvaluationValue(self.BOARD_DATA_tmp)
                    # print(EvalValue)
                    if EvalValue > LatestEvalValue:
                        strategy = (direction0, x0, 1, 1)
                        LatestEvalValue = EvalValue

        # return nextMove
        print("===", datetime.now() - t1)
        nextMove["strategy"]["direction"] = strategy[0]
        nextMove["strategy"]["x"] = strategy[1]
        nextMove["strategy"]["y_operation"] = strategy[2]
        nextMove["strategy"]["y_moveblocknum"] = strategy[3]
        print(nextMove)
        return nextMove


    def getSearchXRange(self, Shape_class, direction):
        #
        # get x range from shape direction.
        #
        minX, maxX, _, _ = Shape_class.getBoundingOffsets(direction)  # get shape x offsets[minX,maxX] as relative value.
        xMin = -1 * minX
        xMax = self.BOARD_DATA.width - maxX
        return xMin, xMax


    def getShapeCoordArray(self, Shape_class, direction, x, y):
        #
        # get coordinate array by given shape.
        #
        coordArray = Shape_class.getCoords(direction, x, y) # get array from shape direction, x, y.
        return coordArray


    def getBoard(self, BOARD_DATA, Shape_class, direction, x):
        #
        # get new board.
        #
        # copy backboard data to make new board.
        # if not, original backboard data will be updated later.

        BOARD_DATA_tmp = copy.deepcopy(BOARD_DATA)
        board = self.dropDown(BOARD_DATA_tmp.backBoard, Shape_class, direction, x)
        BOARD_DATA_tmp.backBoard = board
        return BOARD_DATA_tmp


    def dropDown(self, board, Shape_class, direction, x):
        #
        # internal function of getBoard.
        # -- drop down the shape on the board.
        #
        dy = self.BOARD_DATA.height - 1
        coordArray = self.getShapeCoordArray(Shape_class, direction, x, 0)
        # update dy
        for _x, _y in coordArray:
            _yy = 0
            while _yy + _y < self.BOARD_DATA.height and (_yy + _y < 0 or board[(_y + _yy) * self.BOARD_DATA.width + _x] == self.ShapeNone_index):
                _yy += 1
            _yy -= 1
            if _yy < dy:
                dy = _yy
        # get new board
        _board = self.dropDownWithDy(board, Shape_class, direction, x, dy)
        return _board


    def dropDownWithDy(self, board, Shape_class, direction, x, dy):
        #
        # internal function of dropDown.
        #
        _board = board
        coordArray = self.getShapeCoordArray(Shape_class, direction, x, 0)
        for _x, _y in coordArray:
            _board[(_y + dy) * self.BOARD_DATA.width + _x] = Shape_class.shape
        return _board


    def calcEvaluationValue(self, BOARD_DATA):

        sum_nholes = get_sum_nholes(BOARD_DATA)
        bumpiness = get_bumpiness(BOARD_DATA)
        max_peak = get_max_peak(BOARD_DATA)
        max_well = get_max_well(BOARD_DATA)

        score = 0
        score -= sum_nholes * 10.0
        score -= bumpiness * 1.0
        #score -= max_peak * 1
        #score -= max_well * 1

        return score


BLOCK_CONTROLLER = Block_Controller()

