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
    def GetNextMove(self, nextMove, GameStatus):

        t1 = datetime.now()

        # print GameStatus
        print("=================================================>")
        # pprint.pprint(GameStatus, width=61, compact=True)

        width = GameStatus["field_info"]["width"]
        width_9cols = width - 1
        height = GameStatus["field_info"]["height"]
        self.backboard = copy.deepcopy(GameStatus["field_info"]["backboard"])
        backBoard2d = get_backBoard2d(self.backboard, width)
        backBoard2d_9cols = backBoard2d[:, :-1]
        self.backboard = get_backBoard1d(backBoard2d_9cols)
        # 10列目のpeak
        col10_peak = get_peaks_per_col(GameStatus["field_info"]["backboard"], width)[width - 1]
        #  #                   ##             ##
        # ### -> (0, 1, 2, 3)   ## -> (0, 1)  ## -> (0)
        CurrentShapeDirectionRange = GameStatus["block_info"]["currentShape"]["direction_range"]
        # Shape() クラス
        self.CurrentShape_class = GameStatus["block_info"]["currentShape"]["class"]
        NextShapeDirectionRange = GameStatus["block_info"]["nextShape"]["direction_range"]
        self.NextShape_class = GameStatus["block_info"]["nextShape"]["class"]
        # 0
        self.ShapeNone_index = GameStatus["debug_info"]["shape_info"]["shapeNone"]["index"]

        if self.CurrentShape_class.shape == 1 and whether_can_put_I_in(self.backboard, width_9cols, height, col10_peak):
            strategy = (0, width - 1, 1, 1)
        else:
            LatestEvalValue = -100000
            strategy = (0, 5, 1, 1)
            for direction0 in CurrentShapeDirectionRange:
                x0Min, x0Max = self.getSearchXRange(width_9cols, self.CurrentShape_class, direction0)
                for x0 in range(x0Min, x0Max):
                    self.backboard_tmp = self.getBoard(self.backboard, width_9cols, height, self.CurrentShape_class, direction0, x0)

                    if self.NextShape_class.shape == 1 and whether_can_put_I_in(self.backboard_tmp, width_9cols, height, col10_peak):
                        EvalValue = self.calcEvaluationValue(self.backboard_tmp, width_9cols, height)
                        if EvalValue > LatestEvalValue:
                            strategy = (direction0, x0, 1, 1)
                            LatestEvalValue = EvalValue
                    else:
                        for direction1 in NextShapeDirectionRange:
                            x1Min, x1Max = self.getSearchXRange(width_9cols, self.NextShape_class, direction1)
                            for x1 in range(x1Min, x1Max):
                                self.backboard_tmp2 = self.getBoard(self.backboard_tmp, width_9cols, height, self.NextShape_class, direction1, x1)

                                EvalValue = self.calcEvaluationValue(self.backboard_tmp2, width_9cols, height)
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


    def getSearchXRange(self, width, Shape_class, direction):
        #
        # get x range from shape direction.
        #
        minX, maxX, _, _ = Shape_class.getBoundingOffsets(direction)  # get shape x offsets[minX,maxX] as relative value.
        xMin = -1 * minX
        xMax = width - maxX
        return xMin, xMax


    def getShapeCoordArray(self, Shape_class, direction, x, y):
        #
        # get coordinate array by given shape.
        #
        coordArray = Shape_class.getCoords(direction, x, y) # get array from shape direction, x, y.
        return coordArray


    def getBoard(self, backboard, width, height, Shape_class, direction, x):
        #
        # get new board.
        #
        # copy backboard data to make new board.
        # if not, original backboard data will be updated later.

        backboard_tmp = copy.deepcopy(backboard)
        backboard_tmp = self.dropDown(backboard_tmp, width, height, Shape_class, direction, x)
        return backboard_tmp


    def dropDown(self, board, width, height, Shape_class, direction, x):
        #
        # internal function of getBoard.
        # -- drop down the shape on the board.
        #
        dy = height - 1
        coordArray = self.getShapeCoordArray(Shape_class, direction, x, 0)
        # update dy
        for _x, _y in coordArray:
            _yy = 0
            while _yy + _y < height and (_yy + _y < 0 or board[(_y + _yy) * width + _x] == self.ShapeNone_index):
                _yy += 1
            _yy -= 1
            if _yy < dy:
                dy = _yy
        # get new board
        _board = self.dropDownWithDy(board, width, Shape_class, direction, x, dy)
        return _board


    def dropDownWithDy(self, board, width, Shape_class, direction, x, dy):
        #
        # internal function of dropDown.
        #
        _board = board
        coordArray = self.getShapeCoordArray(Shape_class, direction, x, 0)
        for _x, _y in coordArray:
            _board[(_y + dy) * width + _x] = Shape_class.shape
        return _board


    def calcEvaluationValue(self, backboard, width, height):

        sum_nholes = get_sum_nholes(backboard, width)
        row_transition = get_row_transition(backboard, width)
        bumpiness = get_bumpiness(backboard, width)
        max_peak = get_max_peak(backboard, width)
        min_peak3 = get_min_peak3(backboard, width)
        max_well = get_max_well(backboard, width)
        wells2 = get_wells2(backboard, width, height)

        score = 0
        score -= sum_nholes * 100
        score -= row_transition * 0.1
        score -= bumpiness * 1
        score -= max_peak * 10
        score += min_peak3[0] * 10
        score += min_peak3[1] * 5
        score += min_peak3[2] * 1
        score -= max_well * 10
        for i, w in enumerate(wells2):
            if w >= 3:
                score -= w * 50
            else:
                score -= w * 10

        return score


BLOCK_CONTROLLER = Block_Controller()
